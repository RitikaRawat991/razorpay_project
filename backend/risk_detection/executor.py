from dataclasses import dataclass

from backend.razorpay.client import RazorpayClient


@dataclass
class ExecutionResult:
    executed: bool
    action: str
    message: str
    external_reference: str | None = None
    payment_status: str = "failed"


class RecoveryActionExecutor:

    APPROVED_ACTIONS = {
        "retry_payment",
        "retry_alternate_method",
        "request_customer_action",
    }

    def __init__(self):
        self.razorpay_client = RazorpayClient()

    def execute(
        self,
        action: str,
        guard_allowed: bool,
        payment_id: str | None = None,
        amount: int = 0,
    ) -> ExecutionResult:

        if not guard_allowed:
            return ExecutionResult(
                executed=False,
                action=action,
                message="action blocked by recovery guard",
            )

        if action not in self.APPROVED_ACTIONS:
            return ExecutionResult(
                executed=False,
                action=action,
                message="action is not approved for execution",
            )

        if not payment_id:
            return ExecutionResult(
                executed=False,
                action=action,
                message="payment_id is required for recovery execution",
            )

        if action == "retry_payment":
            result = self.razorpay_client.retry_payment(
                payment_id=payment_id,
                amount=amount,
            )

        elif action == "retry_alternate_method":
            result = self.razorpay_client.retry_alternate_method(
                payment_id=payment_id,
                amount=amount,
            )

        else:
            result = self.razorpay_client.request_customer_action(
                payment_id=payment_id,
            )

        return ExecutionResult(
            executed=result.success,
            action=result.action,
            message=result.message,
            external_reference=result.external_reference,
            payment_status=result.payment_status,
        )