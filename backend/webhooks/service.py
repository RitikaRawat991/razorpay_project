from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from datetime import datetime

from backend.database.models import (
    Payment,
    RecoveryAction,
    RecoveryOpportunity,
    RecoveryOutcome,
)
from backend.risk_detection.learning import RecoveryLearningService
from backend.risk_detection.merchant_learning import MerchantLearningService
from backend.revenue_monitor.events import PaymentEvent
from backend.risk_detection.service import RiskDetectionService
from backend.webhooks.schemas import RazorpayPaymentWebhook


class RazorpayWebhookService:

    def process_captured_recovery(
        self,
        db: Session,
        payment_id: str,
        order_id: str | None,
        amount: int,
    ) -> dict:
        """Verify a captured payment only when it belongs to a recovery order."""
        if not order_id:
            return {"status": "ignored", "message": "captured payment has no order_id"}

        action = (
            db.query(RecoveryAction)
            .filter(RecoveryAction.razorpay_order_id == order_id)
            .first()
        )
        if action is None:
            return {"status": "ignored", "message": "captured payment is not a RecoverIQ recovery"}

        if action.status == "recovered":
            return {"status": "duplicate", "action_id": action.id}

        outcome = (
            db.query(RecoveryOutcome)
            .filter(RecoveryOutcome.action_id == action.id)
            .order_by(RecoveryOutcome.id.desc())
            .first()
        )
        if outcome is None:
            outcome = RecoveryOutcome(action_id=action.id, outcome="awaiting_confirmation")
            db.add(outcome)

        action.razorpay_payment_id = payment_id
        action.status = "recovered"
        action.executed_at = action.executed_at or datetime.utcnow()
        outcome.outcome = "recovered"
        outcome.recovered_amount = amount
        outcome.failure_reason = None
        outcome.verified_at = datetime.utcnow()

        opportunity = db.get(RecoveryOpportunity, action.opportunity_id)
        if opportunity is not None:
            opportunity.status = "recovered"

        db.commit()
        db.refresh(outcome)

        learning = RecoveryLearningService().learn_from_outcome(db=db, outcome=outcome)
        if opportunity is not None:
            original_payment = db.get(Payment, opportunity.payment_id)
            if original_payment is not None:
                MerchantLearningService().learn(db=db, merchant_id=original_payment.merchant_id)

        return {"status": "recovered", "action_id": action.id, "outcome_id": outcome.id, "learning": learning}

    def process_payment_webhook(
        self,
        db: Session,
        payload: RazorpayPaymentWebhook,
    ) -> dict:

        # Check whether this Razorpay payment was already processed
        existing_payment = (
            db.query(Payment)
            .filter(Payment.payment_id == payload.payment_id)
            .first()
        )

        if existing_payment is not None:
            return {
                "status": "duplicate",
                "message": "payment webhook already processed",
                "payment_id": existing_payment.id,
                "razorpay_payment_id": existing_payment.payment_id,
            }

        payment = Payment(
            payment_id=payload.payment_id,
            merchant_id=payload.merchant_id,
            amount=payload.amount,
            currency="INR",
            status=payload.status,
            failure_reason=payload.failure_reason,
            created_at=payload.created_at,
        )

        db.add(payment)

        try:
            db.commit()
            db.refresh(payment)

        except IntegrityError:
            db.rollback()

            existing_payment = (
                db.query(Payment)
                .filter(Payment.payment_id == payload.payment_id)
                .first()
            )

            if existing_payment is not None:
                return {
                    "status": "duplicate",
                    "message": "payment webhook already processed",
                    "payment_id": existing_payment.id,
                    "razorpay_payment_id": existing_payment.payment_id,
                }

            raise

        event = PaymentEvent(
            payment_id=payload.payment_id,
            merchant_id=payload.merchant_id,
            customer_id=payload.customer_id,
            amount=payload.amount,
            status=payload.status,
            method=payload.method,
            created_at=payload.created_at,
            failure_reason=payload.failure_reason,
        )

        result = RiskDetectionService().evaluate(
            db=db,
            event=event,
            database_payment_id=payment.id,
        )

        return {
            "status": "processed",
            "payment_id": payment.id,
            "razorpay_payment_id": payload.payment_id,
            "risk": result["risk"],
            "diagnosis": result["diagnosis"],
            "prediction": result["prediction"],
            "guard": result["guard"],
            "execution": result["execution"],
            "verification": result["verification"],
            "opportunity": result["opportunity"],
            "recovery_action": result["recovery_action"],
            "recovery_outcome": result["recovery_outcome"],
        }
