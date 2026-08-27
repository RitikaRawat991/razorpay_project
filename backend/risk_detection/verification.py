from dataclasses import dataclass


@dataclass
class RecoveryVerification:
    verified: bool
    recovered: bool
    recovered_amount: int
    message: str


class RecoveryVerifier:

    SUCCESS_STATUSES = {
        "success",
        "captured",
        "paid",
        "completed",
    }

    FAILED_STATUSES = {
        "failed",
        "failure",
        "cancelled",
        "canceled",
    }

    PENDING_STATUSES = {
        "pending",
        "processing",
        "created",
    }

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

        status = payment_status.lower().strip()

        # Payment was successfully recovered
        if status in self.SUCCESS_STATUSES:
            return RecoveryVerification(
                verified=True,
                recovered=True,
                recovered_amount=amount,
                message="payment recovered successfully",
            )

        # Payment is still not successful
        if status in self.FAILED_STATUSES | self.PENDING_STATUSES:
            return RecoveryVerification(
                verified=True,
                recovered=False,
                recovered_amount=0,
                message=(
                    f"recovery action executed but payment "
                    f"status is still {payment_status}"
                ),
            )

        # Unknown payment status
        return RecoveryVerification(
            verified=False,
            recovered=False,
            recovered_amount=0,
            message=(
                f"unable to verify unknown payment status: "
                f"{payment_status}"
            ),
        )