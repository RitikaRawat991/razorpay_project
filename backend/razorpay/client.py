from dataclasses import dataclass


@dataclass
class RazorpayActionResult:
    success: bool
    action: str
    message: str
    external_reference: str | None = None


class RazorpayClient:
    """
    Abstraction layer for Razorpay payment operations.

    This keeps external Razorpay integration separate from
    the recovery decision and execution logic.
    """

    def retry_payment(
        self,
        payment_id: str,
        amount: int,
    ) -> RazorpayActionResult:
        """
        Retry a failed payment.

        For now this is a safe integration stub.
        The actual Razorpay API call will be connected here.
        """

        return RazorpayActionResult(
            success=True,
            action="retry_payment",
            message=f"retry request accepted for payment {payment_id}",
            external_reference=payment_id,
        )

    def retry_alternate_method(
        self,
        payment_id: str,
        amount: int,
    ) -> RazorpayActionResult:
        """
        Request recovery through an alternate payment method.
        """

        return RazorpayActionResult(
            success=True,
            action="retry_alternate_method",
            message=(
                f"alternate payment method request accepted "
                f"for payment {payment_id}"
            ),
            external_reference=payment_id,
        )

    def request_customer_action(
        self,
        payment_id: str,
    ) -> RazorpayActionResult:
        """
        Request customer action for payment recovery.
        """

        return RazorpayActionResult(
            success=True,
            action="request_customer_action",
            message=(
                f"customer action request accepted "
                f"for payment {payment_id}"
            ),
            external_reference=payment_id,
        )