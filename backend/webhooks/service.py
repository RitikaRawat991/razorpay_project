from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.models import Payment
from backend.revenue_monitor.events import PaymentEvent
from backend.risk_detection.service import RiskDetectionService
from backend.webhooks.schemas import RazorpayPaymentWebhook


class RazorpayWebhookService:

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