from dataclasses import dataclass


@dataclass
class RecoveryVerification:
    verified: bool
    recovered: bool
    recovered_amount: int
    message: str


class RecoveryVerifier:

    def verify(
        self,
        executed: bool,
        payment_status: str,
        amount: int,
    ) -> RecoveryVerification:

        # Recovery action was not executed
        if not executed:
            return RecoveryVerification(
                verified=True,
                recovered=False,
                recovered_amount=0,
                message="recovery action was not executed",
            )

        # Payment was successfully recovered
        if payment_status == "success":
            return RecoveryVerification(
                verified=True,
                recovered=True,
                recovered_amount=amount,
                message="payment recovered successfully",
            )

        # Recovery action executed, but payment is still failed
        return RecoveryVerification(
            verified=True,
            recovered=False,
            recovered_amount=0,
            message=(
                "recovery action executed but payment "
                "was not recovered"
            ),
        )