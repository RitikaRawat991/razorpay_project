from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.database.models import RecoveryMemory


@dataclass
class LearningResult:
    learned: bool
    recovery_status: str
    attempts: int
    message: str


class RecoveryLearningService:

    def learn(
        self,
        db: Session,
        memory_id: int,
        recovered: bool,
    ) -> LearningResult:

        memory = (
            db.query(RecoveryMemory)
            .filter(RecoveryMemory.id == memory_id)
            .first()
        )

        if memory is None:
            return LearningResult(
                learned=False,
                recovery_status="unknown",
                attempts=0,
                message="recovery memory not found",
            )

        memory.attempts += 1

        if recovered:
            memory.recovery_status = "recovered"
            message = "recovery outcome learned successfully"
        else:
            memory.recovery_status = "failed"
            message = "failed recovery outcome learned successfully"

        db.commit()
        db.refresh(memory)

        return LearningResult(
            learned=True,
            recovery_status=memory.recovery_status,
            attempts=memory.attempts,
            message=message,
        )