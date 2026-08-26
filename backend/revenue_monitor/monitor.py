from dataclasses import dataclass
from datetime import datetime

from backend.risk_detection.detector import RiskDetector

@dataclass
class PaymentEvent:
    payment_id: int
    merchant_id: int
    customer_id: int
    amount: int
    status: str
    method: str
    created_at: datetime
    failure_reason: str | None = None


class RevenueMonitor:
    def __init__(self):
        self.risk_detector = RiskDetector()

    def process_payment(self, event: PaymentEvent) -> dict:
        payment = {
            "payment_id": event.payment_id,
            "merchant_id": event.merchant_id,
            "customer_id": event.customer_id,
            "amount": event.amount,
            "status": event.status,
            "method": event.method,
            "created_at": event.created_at,
        }

        risk = self.risk_detector.assess(payment)

        return {
            "payment": payment,
            "risk": {
                "is_risky": risk.is_risky,
                "risk_score": risk.risk_score,
                "reason": risk.reason,
            },
        }