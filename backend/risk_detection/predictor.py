from dataclasses import dataclass


@dataclass
class RecoveryPrediction:
    success_probability: int
    expected_recovery: int
    recommended_action: str


class RecoveryPredictor:

    def predict(
        self,
        amount: int,
        root_cause: str,
        previous_failures: int,
    ) -> RecoveryPrediction:

        success_probability = 50

        if root_cause == "insufficient_funds":
            success_probability = 75

        elif root_cause == "issuer_decline":
            success_probability = 65

        elif root_cause == "payment_failure":
            success_probability = 55

        if previous_failures >= 3:
            success_probability -= 10

        if amount >= 100000:
            success_probability -= 5

        success_probability = max(
            0,
            min(100, success_probability),
        )

        expected_recovery = int(
            amount * success_probability / 100
        )

        if root_cause == "insufficient_funds":
            recommended_action = "retry_payment"

        elif root_cause == "issuer_decline":
            recommended_action = "retry_alternate_method"

        else:
            recommended_action = "request_customer_action"

        return RecoveryPrediction(
            success_probability=success_probability,
            expected_recovery=expected_recovery,
            recommended_action=recommended_action,
        )