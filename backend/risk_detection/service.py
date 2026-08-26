from sqlalchemy.orm import Session

from backend.revenue_monitor.monitor import PaymentEvent
from backend.risk_detection.detector import RiskDetector
from backend.risk_detection.history import get_previous_failure_count
from backend.risk_detection.opportunity import create_recovery_opportunity
from backend.risk_detection.scorer import OpportunityScorer


class RiskDetectionService:
    def __init__(self):
        self.detector = RiskDetector()
        self.scorer = OpportunityScorer()

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
        opportunity_score = None
        previous_failures = 0

        if risk.is_risky:
            previous_failures = get_previous_failure_count(
                db=db,
                merchant_id=event.merchant_id,
                payment_id=database_payment_id,
            )

            opportunity_score = self.scorer.calculate(
                risk_score=risk.risk_score,
                amount=event.amount,
                previous_failures=previous_failures,
            )

            opportunity = create_recovery_opportunity(
                db=db,
                payment_id=database_payment_id,
                customer_id=event.customer_id,
                risk_score=opportunity_score.score,
                reason=risk.reason,
            )

        return {
            "payment": payment,
            "risk": risk,
            "previous_failures": previous_failures,
            "opportunity_score": opportunity_score,
            "opportunity": opportunity,
        }