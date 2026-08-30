import razorpay
from dataclasses import dataclass

from backend.api.config import settings


@dataclass
class RazorpayActionResult:
    success: bool
    action: str
    message: str
    external_reference: str | None = None
    payment_status: str = "pending"
    key_id: str | None = None


class RazorpayClient:
    """
    Real Razorpay test-mode integration.

    RecoverIQ does NOT mark a payment as recovered itself.
    It creates a new Razorpay order for the recovery attempt.

    The actual payment result is confirmed later through
    Razorpay's payment webhook.
    """

    def __init__(self):
        if not settings.RAZORPAY_KEY_ID:
            raise RuntimeError(
                "RAZORPAY_KEY_ID is not configured"
            )

        if not settings.RAZORPAY_KEY_SECRET:
            raise RuntimeError(
                "RAZORPAY_KEY_SECRET is not configured"
            )

        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

    def retry_payment(
        self,
        payment_id: str,
        amount: int,
    ) -> RazorpayActionResult:

        try:
            order = self.client.order.create(
                {
                    "amount": amount,
                    "currency": "INR",
                    "receipt": f"recoveriq_{payment_id}",
                    "notes": {
                        "recoveriq_recovery": "true",
                        "original_payment_id": payment_id,
                    },
                }
            )

            return RazorpayActionResult(
                success=True,
                action="retry_payment",
                message=(
                    f"Recovery payment order created for "
                    f"failed payment {payment_id}"
                ),
                external_reference=order["id"],
                payment_status="pending",
                key_id=settings.RAZORPAY_KEY_ID,
            )

        except Exception as exc:
            return RazorpayActionResult(
                success=False,
                action="retry_payment",
                message=f"Unable to create recovery order: {exc}",
                external_reference=None,
                payment_status="failed",
                key_id=settings.RAZORPAY_KEY_ID,
            )

    def retry_alternate_method(
        self,
        payment_id: str,
        amount: int,
    ) -> RazorpayActionResult:

        return self.retry_payment(
            payment_id=payment_id,
            amount=amount,
        )

    def request_customer_action(
        self,
        payment_id: str,
    ) -> RazorpayActionResult:

        return RazorpayActionResult(
            success=True,
            action="request_customer_action",
            message=(
                f"Customer action required for payment "
                f"{payment_id}"
            ),
            external_reference=payment_id,
            payment_status="pending",
            key_id=settings.RAZORPAY_KEY_ID,
        )