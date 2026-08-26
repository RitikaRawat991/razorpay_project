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

        if not executed:
            return RecoveryVerification(
                verified=True,
                recovered=False,
                recovered_amount=0,
                message="recovery action was not executed",
            )

        if payment_status == "success":
            return RecoveryVerification(
                verified=True,
                recovered=True,
                recovered_amount=amount,
                message="payment recovered successfully",
            )

        return RecoveryVerification(
            verified=True,
            recovered=False,
            recovered_amount=0,
            message="recovery action executed but payment was not recovered",
        )