from sqlalchemy.orm import Session

from backend.revenue_monitor.monitor import PaymentEvent
from backend.risk_detection.opportunity import create_recovery_opportunity
from backend.risk_detection.detector import RiskDetector


class RiskDetectionService:
    def __init__(self):
        self.detector = RiskDetector()

    def evaluate(
        self,
        db: Session,
        event: PaymentEvent,
        database_payment_id: int,
    ):
        payment = {
            "payment_id": event.payment_id,
            "merchant_id": event.merchant_id,
            "customer_id": event.customer_id,
            "amount": event.amount,
            "status": event.status,
            "method": event.method,
            "created_at": event.created_at,
        }

        risk = self.detector.assess(payment)

        opportunity = None

        if risk.is_risky:
            opportunity = create_recovery_opportunity(
                db=db,
                payment_id=database_payment_id,
                customer_id=event.customer_id,
                risk_score=risk.risk_score,
                reason=risk.reason,
            )

        return {
            "payment": payment,
            "risk": risk,
            "opportunity": opportunity,
        }