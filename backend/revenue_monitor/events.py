from dataclasses import dataclass
from datetime import datetime


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