import razorpay
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.config import settings
from backend.database.connection import get_db
from backend.database.models import Payment, RecoveryAction, RecoveryOpportunity
from backend.razorpay.client import RazorpayClient
from backend.webhooks.schemas import RazorpayPaymentWebhook
from backend.webhooks.service import RazorpayWebhookService


router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
)


@router.get("/recovery-checkout/{action_id}")
def get_recovery_checkout(
    action_id: int,
    db: Session = Depends(get_db),
):
    """Return checkout-safe data only for an executed recovery order."""
    action = db.get(RecoveryAction, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Recovery action not found")
    if action.status != "executed" or not action.razorpay_order_id:
        raise HTTPException(
            status_code=409,
            detail="Recovery action is not awaiting customer payment",
        )

    opportunity = db.get(RecoveryOpportunity, action.opportunity_id)
    payment = db.get(Payment, opportunity.payment_id) if opportunity else None
    if payment is None:
        raise HTTPException(status_code=404, detail="Original payment not found")

    return {
        "action_id": action.id,
        "order_id": action.razorpay_order_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "key_id": settings.RAZORPAY_KEY_ID,
        "description": "Complete your RecoverIQ payment recovery",
    }


@router.post("/recovery-actions/{action_id}/verify")
def reconcile_recovery_payment(
    action_id: int,
    db: Session = Depends(get_db),
):
    """Reconcile a missed webhook against Razorpay's authoritative order data."""
    action = db.get(RecoveryAction, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Recovery action not found")
    if action.status == "recovered":
        return {"status": "duplicate", "action_id": action.id}
    if not action.razorpay_order_id:
        raise HTTPException(status_code=409, detail="Recovery order is unavailable")

    try:
        payments = RazorpayClient().client.order.payments(
            action.razorpay_order_id
        ).get("items", [])
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to verify recovery payment: {exc}",
        )

    captured = next(
        (payment for payment in payments if payment.get("status") == "captured"),
        None,
    )
    if captured is None:
        return {
            "status": "awaiting_confirmation",
            "action_id": action.id,
            "message": "Razorpay has not captured a recovery payment yet",
        }

    return RazorpayWebhookService().process_captured_recovery(
        db=db,
        payment_id=str(captured["id"]),
        order_id=action.razorpay_order_id,
        amount=int(captured["amount"]),
    )


@router.post("/failed/{payment_id}/reconcile")
def reconcile_failed_payment(
    payment_id: str,
    merchant_id: int = 1,
    customer_id: int = 1,
    db: Session = Depends(get_db),
):
    """Verify a Checkout failure with Razorpay before starting recovery."""
    try:
        payment = RazorpayClient().client.payment.fetch(payment_id)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to verify failed payment: {exc}",
        )

    if payment.get("status") != "failed":
        raise HTTPException(
            status_code=409,
            detail="Razorpay has not confirmed this payment as failed",
        )

    notes = payment.get("notes") or {}
    try:
        merchant_id = int(notes.get("merchant_id", merchant_id))
        customer_id = int(notes.get("customer_id", customer_id))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Invalid payment metadata")

    payload = RazorpayPaymentWebhook(
        payment_id=str(payment["id"]),
        merchant_id=merchant_id,
        customer_id=customer_id,
        amount=int(payment["amount"]),
        status="failed",
        method=str(payment.get("method") or "unknown"),
        created_at=datetime.fromtimestamp(payment.get("created_at", 0)),
        failure_reason=(
            payment.get("error_reason")
            or payment.get("error_description")
            or payment.get("error_code")
            or "payment_failed"
        ),
    )
    return RazorpayWebhookService().process_payment_webhook(db=db, payload=payload)


@router.post("/create-order")
def create_order(
    amount: int,
    currency: str = "INR",
    merchant_id: int = 1,
    customer_id: int = 1,
):
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Razorpay API credentials are not configured",
        )

    try:
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

        order = client.order.create(
            {
                "amount": amount,
                "currency": currency,
                "receipt": f"recoveriq_{amount}",
                "notes": {
                    "merchant_id": str(merchant_id),
                    "customer_id": str(customer_id),
                },
            }
        )

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": settings.RAZORPAY_KEY_ID,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to create Razorpay order: {str(exc)}",
        )
