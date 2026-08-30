import hashlib
import hmac
import json
from datetime import datetime

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
    db: Session = Depends(get_db),
    x_razorpay_signature: str | None = Header(
        default=None,
        alias="X-Razorpay-Signature",
    ),
):
    # ------------------------------------------------------------
    # 1. Verify Razorpay signature
    # ------------------------------------------------------------

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

    # ------------------------------------------------------------
    # 2. Parse webhook JSON
    # ------------------------------------------------------------

    try:
        webhook_data = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook JSON",
        )

    event = webhook_data.get("event")

    # ------------------------------------------------------------
    # 3. We only trigger recovery for payment.failed
    # ------------------------------------------------------------

    if event != "payment.failed":
        return {
            "status": "ignored",
            "result": {
                "event": event,
                "message": "Webhook event not handled",
            },
        }

    # ------------------------------------------------------------
    # 4. Extract Razorpay payment entity
    # ------------------------------------------------------------

    payment_entity = (
        webhook_data
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    if not payment_entity:
        raise HTTPException(
            status_code=400,
            detail="Payment entity missing from Razorpay webhook",
        )

    # ------------------------------------------------------------
    # 5. Extract merchant/customer metadata
    # ------------------------------------------------------------

    notes = payment_entity.get("notes") or {}

    merchant_id = notes.get("merchant_id", 1)
    customer_id = notes.get("customer_id", 1)

    try:
        merchant_id = int(merchant_id)
        customer_id = int(customer_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail="Invalid merchant_id or customer_id in payment notes",
        )

    # ------------------------------------------------------------
    # 6. Extract actual Razorpay failure reason
    # ------------------------------------------------------------

    failure_reason = (
        payment_entity.get("error_reason")
        or payment_entity.get("error_description")
        or payment_entity.get("error_code")
        or "payment_failed"
    )

    # ------------------------------------------------------------
    # 7. Convert Razorpay timestamp
    # ------------------------------------------------------------

    created_at_timestamp = payment_entity.get("created_at")

    try:
        created_at = datetime.fromtimestamp(
            int(created_at_timestamp)
        )
    except (TypeError, ValueError, OSError):
        created_at = datetime.now()

    # ------------------------------------------------------------
    # 8. Normalize Razorpay payload into RecoverIQ schema
    # ------------------------------------------------------------

    try:
        internal_payload = RazorpayPaymentWebhook(
            payment_id=str(payment_entity.get("id")),
            merchant_id=merchant_id,
            customer_id=customer_id,
            amount=int(payment_entity.get("amount", 0)),
            status=payment_entity.get("status", "failed"),
            method=payment_entity.get("method", "unknown"),
            created_at=created_at,
            failure_reason=str(failure_reason),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to map Razorpay webhook: {str(exc)}",
        )

    # ------------------------------------------------------------
    # 9. Send normalized payment into RecoverIQ pipeline
    # ------------------------------------------------------------

    result = RazorpayWebhookService().process_payment_webhook(
        db=db,
        payload=internal_payload,
    )

    # ------------------------------------------------------------
    # 10. Return successful webhook response
    # ------------------------------------------------------------

    return {
        "status": "processed",
        "result": result,
    }