import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from backend.api.config import settings
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
async def razorpay_payment_webhook(
    request: Request,
    payload: RazorpayPaymentWebhook,
    db: Session = Depends(get_db),
    x_razorpay_signature: str | None = Header(
        default=None,
        alias="X-Razorpay-Signature",
    ),
):
    if not x_razorpay_signature:
        raise HTTPException(
            status_code=401,
            detail="Missing Razorpay webhook signature",
        )

    raw_body = await request.body()

    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        x_razorpay_signature,
        expected_signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Razorpay webhook signature",
        )

    result = RazorpayWebhookService().process_payment_webhook(
        db=db,
        payload=payload,
    )

    return {
        "status": "processed",
        "result": result,
    }