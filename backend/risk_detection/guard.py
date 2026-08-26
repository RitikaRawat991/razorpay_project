from dataclasses import dataclass


@dataclass
class GuardDecision:
    allowed: bool
    reason: str
    action: str


class RecoveryGuard:

    def check(
        self,
        action: str,
        confidence: int,
        recoverable: bool,
        amount: int,
    ) -> GuardDecision:

        if not recoverable:
            return GuardDecision(
                allowed=False,
                reason="root cause is not recoverable",
                action=action,
            )

        if confidence < 60:
            return GuardDecision(
                allowed=False,
                reason="diagnosis confidence is too low",
                action=action,
            )

        if amount > 500000:
            return GuardDecision(
                allowed=False,
                reason="amount exceeds automated recovery limit",
                action=action,
            )

        allowed_actions = {
            "retry_payment",
            "retry_alternate_method",
            "request_customer_action",
        }

        if action not in allowed_actions:
            return GuardDecision(
                allowed=False,
                reason="action is not approved for automated execution",
                action=action,
            )

        return GuardDecision(
            allowed=True,
            reason="action passed all recovery safety checks",
            action=action,
        )