from dataclasses import dataclass


@dataclass
class ExecutionResult:
    executed: bool
    action: str
    message: str


class RecoveryActionExecutor:

    APPROVED_ACTIONS = {
        "retry_payment",
        "retry_alternate_method",
        "request_customer_action",
    }

    def execute(
        self,
        action: str,
        guard_allowed: bool,
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

        return ExecutionResult(
            executed=True,
            action=action,
            message=f"{action} execution accepted",
        )