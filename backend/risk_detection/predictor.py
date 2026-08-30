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
        merchant_recovery_rate: float = 0.0,
    ) -> RecoveryPrediction:

        # ---------------------------------------------------------
        # 1. Base probability from root cause
        # ---------------------------------------------------------

        if root_cause == "insufficient_funds":
            base_probability = 75

        elif root_cause == "issuer_decline":
            base_probability = 65

        elif root_cause == "payment_failure":
            base_probability = 55

        else:
            base_probability = 50

        # ---------------------------------------------------------
        # 2. Historical failure penalty
        # ---------------------------------------------------------

        if previous_failures >= 3:
            base_probability -= 10

        # ---------------------------------------------------------
        # 3. High-value payment penalty
        # ---------------------------------------------------------

        if amount >= 100000:
            base_probability -= 5

        # ---------------------------------------------------------
        # 4. Merchant-level learning
        # ---------------------------------------------------------

        merchant_rate = max(
            0.0,
            min(1.0, merchant_recovery_rate),
        )

        merchant_probability = merchant_rate * 100

        success_probability = (
            base_probability * 0.70
            + merchant_probability * 0.30
        )

        success_probability = int(
            round(success_probability)
        )

        # ---------------------------------------------------------
        # 5. Safety bounds
        # ---------------------------------------------------------

        success_probability = max(
            0,
            min(100, success_probability),
        )

        # ---------------------------------------------------------
        # 6. Expected recovery
        # ---------------------------------------------------------

        expected_recovery = int(
            amount * success_probability / 100
        )

        # ---------------------------------------------------------
        # 7. Recommended action
        # ---------------------------------------------------------

        if root_cause in {
            "insufficient_funds",
            "payment_failure",
        }:
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