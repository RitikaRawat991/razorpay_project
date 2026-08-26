from sqlalchemy.orm import Session

from backend.revenue_monitor.events import PaymentEvent
from backend.risk_detection.service import RiskDetectionService


class RevenueMonitor:
    def __init__(self):
        self.risk_detection_service = RiskDetectionService()

    def process_payment(
        self,
        db: Session,
        event: PaymentEvent,
        database_payment_id: int,
    ) -> dict:

        result = self.risk_detection_service.evaluate(
            db=db,
            event=event,
            database_payment_id=database_payment_id,
        )

        return result