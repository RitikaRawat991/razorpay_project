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


class RecoveryResponse(BaseModel):
    executed: bool
    action: str
    message: str
    external_reference: str | None = None


class VerificationResponse(BaseModel):
    verified: bool
    recovered: bool
    recovered_amount: int
    message: str


class WebhookResponse(BaseModel):
    status: str
    result: dict