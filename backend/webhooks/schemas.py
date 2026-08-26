from datetime import datetime

from pydantic import BaseModel, Field


class RazorpayPaymentWebhook(BaseModel):
    payment_id: str = Field(..., min_length=1)
    merchant_id: int
    customer_id: int
    amount: int = Field(..., gt=0)
    status: str
    method: str
    created_at: datetime
    failure_reason: str | None = None