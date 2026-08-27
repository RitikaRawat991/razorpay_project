from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.database.models import Payment, RecoveryMemory


@dataclass
class MerchantLearningResult:
    merchant_id: int
    total_recoveries: int
    total_failures: int
    recovery_rate: float
    message: str


class MerchantLearningService:

    def learn(
        self,
        db: Session,
        merchant_id: int,
    ) -> MerchantLearningResult:

        # Get all recovery memories belonging to this merchant.
        # RecoveryMemory -> Payment -> merchant_id
        memories = (
            db.query(RecoveryMemory)
            .join(
                Payment,
                RecoveryMemory.payment_id == Payment.id,
            )
            .filter(
                Payment.merchant_id == merchant_id
            )
            .all()
        )

        # Count successful recoveries.
        total_recoveries = sum(
            1
            for memory in memories
            if memory.recovery_status == "recovered"
        )

        # Count failed recoveries.
        total_failures = sum(
            1
            for memory in memories
            if memory.recovery_status == "failed"
        )

        # Ignore pending memories when calculating
        # the actual recovery rate.
        total_outcomes = (
            total_recoveries + total_failures
        )

        recovery_rate = (
            total_recoveries / total_outcomes
            if total_outcomes > 0
            else 0.0
        )

        return MerchantLearningResult(
            merchant_id=merchant_id,
            total_recoveries=total_recoveries,
            total_failures=total_failures,
            recovery_rate=round(recovery_rate, 2),
            message="merchant recovery pattern analyzed",
        )