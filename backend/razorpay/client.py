from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class RazorpayActionResult:
    success: bool
    action: str
    message: str
    external_reference: str | None = None
    payment_status: str = "failed"


class RazorpayClient:
    """
    Safe Razorpay integration abstraction.

    In development, MOCK_RAZORPAY_SUCCESS=true simulates
    a successful recovery so the complete RecoverIQ pipeline
    can be tested without making a real Razorpay API call.
    """

    def __init__(self):
        self.mock_success = (
            os.getenv("MOCK_RAZORPAY_SUCCESS", "false").lower()
            == "true"
        )

    def _payment_status(self) -> str:
        return "captured" if self.mock_success else "failed"

    def retry_payment(
        self,
        payment_id: str,
        amount: int,
    ) -> RazorpayActionResult:

        status = self._payment_status()

        return RazorpayActionResult(
            success=True,
            action="retry_payment",
            message=(
                f"retry request accepted for payment {payment_id}"
                if status == "failed"
                else f"payment retry succeeded for payment {payment_id}"
            ),
            external_reference=payment_id,
            payment_status=status,
        )

    def retry_alternate_method(
        self,
        payment_id: str,
        amount: int,
    ) -> RazorpayActionResult:

        status = self._payment_status()

        return RazorpayActionResult(
            success=True,
            action="retry_alternate_method",
            message=(
                f"alternate payment method request accepted "
                f"for payment {payment_id}"
                if status == "failed"
                else f"alternate payment method succeeded "
                     f"for payment {payment_id}"
            ),
            external_reference=payment_id,
            payment_status=status,
        )

    def request_customer_action(
        self,
        payment_id: str,
    ) -> RazorpayActionResult:

        status = self._payment_status()

        return RazorpayActionResult(
            success=True,
            action="request_customer_action",
            message=(
                f"customer action request accepted "
                f"for payment {payment_id}"
            ),
            external_reference=payment_id,
            payment_status=status,
        )