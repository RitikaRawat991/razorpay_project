from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.webhooks.schemas import (
    RazorpayPaymentWebhook,
    WebhookResponse,
)
from backend.webhooks.service import RazorpayWebhookService


router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"],
)


@router.post(
    "/razorpay/payment",
    response_model=WebhookResponse,
)
def razorpay_payment_webhook(
    payload: RazorpayPaymentWebhook,
    db: Session = Depends(get_db),
):
    result = RazorpayWebhookService().process_payment_webhook(
        db=db,
        payload=payload,
    )

    return {
        "status": "processed",
        "result": result,
    }