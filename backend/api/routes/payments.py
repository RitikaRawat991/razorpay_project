import razorpay
from fastapi import APIRouter, HTTPException

from backend.api.config import settings


router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
)


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