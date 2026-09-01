import hashlib
import hmac
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.api.config import settings
from backend.api.main import app
from backend.database.connection import get_db
from backend.database.base import Base
from backend.database.models import (
    Customer,
    Merchant,
    Payment,
    RecoveryAction,
    RecoveryOpportunity,
    RecoveryOutcome,
)
from backend.razorpay.client import RazorpayActionResult
from backend.risk_detection.action import create_recovery_action
from backend.risk_detection.executor import RecoveryActionExecutor
from backend.risk_detection.outcome import create_recovery_outcome
from backend.webhooks.service import RazorpayWebhookService


class RecoveryLifecycleTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        merchant = Merchant(merchant_id="merchant_test", name="Test merchant")
        self.db.add(merchant)
        self.db.commit()
        customer = Customer(
            customer_id="customer_test", merchant_id=merchant.id,
        )
        self.db.add(customer)
        self.db.commit()
        payment = Payment(
            payment_id="pay_failed", merchant_id=merchant.id, amount=500,
            currency="INR", status="failed", failure_reason="issuer_declined",
        )
        self.db.add(payment)
        self.db.commit()
        self.payment = payment
        self.customer = customer

    def tearDown(self):
        self.db.close()

    def _opportunity(self):
        opportunity = RecoveryOpportunity(
            payment_id=self.payment.id, customer_id=self.customer.id,
            score=80, status="pending_recovery", root_cause="issuer_decline",
        )
        self.db.add(opportunity)
        self.db.commit()
        return opportunity

    def test_action_creation_is_pending(self):
        action = create_recovery_action(
            self.db, self._opportunity().id, "retry_payment", "issuer_decline",
        )
        self.assertEqual(action.status, "pending")
        self.assertIsNone(action.executed_at)
        self.assertIsNone(action.razorpay_order_id)

    def test_executor_forwards_order_reference(self):
        class FakeClient:
            def retry_payment(self, payment_id, amount):
                return RazorpayActionResult(
                    True, "retry_payment", "created", "order_recovery", "pending",
                )

        executor = RecoveryActionExecutor.__new__(RecoveryActionExecutor)
        executor.razorpay_client = FakeClient()
        result = executor.execute("retry_payment", True, "pay_failed", 500)
        self.assertTrue(result.executed)
        self.assertEqual(result.external_reference, "order_recovery")
        self.assertEqual(result.payment_status, "pending")

    def test_captured_payment_recovers_once(self):
        opportunity = self._opportunity()
        action = create_recovery_action(
            self.db, opportunity.id, "retry_payment", "issuer_decline",
        )
        action.status = "executed"
        action.razorpay_order_id = "order_recovery"
        self.db.commit()
        outcome = create_recovery_outcome(
            self.db, action.id, pending=True,
        )
        self.assertEqual(outcome.outcome, "awaiting_confirmation")

        service = RazorpayWebhookService()
        result = service.process_captured_recovery(
            self.db, "pay_recovery", "order_recovery", 500,
        )
        self.assertEqual(result["status"], "recovered")
        self.db.refresh(action)
        self.db.refresh(opportunity)
        self.db.refresh(outcome)
        self.assertEqual(action.razorpay_payment_id, "pay_recovery")
        self.assertEqual(action.status, "recovered")
        self.assertEqual(opportunity.status, "recovered")
        self.assertEqual(outcome.outcome, "recovered")
        self.assertEqual(outcome.recovered_amount, 500)
        self.assertEqual(
            service.process_captured_recovery(
                self.db, "pay_recovery", "order_recovery", 500,
            )["status"],
            "duplicate",
        )

    def test_webhook_signature_capture_and_unsupported_event(self):
        opportunity = self._opportunity()
        action = create_recovery_action(
            self.db, opportunity.id, "retry_payment", "issuer_decline",
        )
        action.status = "executed"
        action.razorpay_order_id = "order_webhook"
        self.db.commit()
        create_recovery_outcome(self.db, action.id, pending=True)

        def override_db():
            yield self.db

        app.dependency_overrides[get_db] = override_db
        client = TestClient(app)

        def post(payload, signature="valid"):
            raw = json.dumps(payload).encode()
            if signature == "valid":
                signature = hmac.new(
                    settings.RAZORPAY_WEBHOOK_SECRET.encode(), raw,
                    hashlib.sha256,
                ).hexdigest()
            return client.post(
                "/api/webhooks/razorpay/payment", content=raw,
                headers={"X-Razorpay-Signature": signature},
            )

        captured = {
            "event": "payment.captured",
            "payload": {"payment": {"entity": {
                "id": "pay_webhook", "order_id": "order_webhook", "amount": 500,
            }}},
        }
        self.assertEqual(post(captured, "not-valid").status_code, 401)
        self.assertEqual(post(captured).json()["status"], "recovered")
        self.assertEqual(post(captured).json()["status"], "duplicate")
        self.assertEqual(
            post({"event": "refund.created"}).json()["status"], "ignored",
        )
        app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()
