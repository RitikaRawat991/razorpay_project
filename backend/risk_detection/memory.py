from sqlalchemy.orm import Session

from backend.database.models import RecoveryMemory


class RecoveryMemoryService:

    def record(
        self,
        db: Session,
        customer_id: int,
        payment_id: int,
        root_cause: str,
    ) -> RecoveryMemory:

        memory = RecoveryMemory(
            customer_id=customer_id,
            payment_id=payment_id,
            root_cause=root_cause,
            recovery_status="pending",
            attempts=0,
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        return memory

    def get_customer_history(
        self,
        db: Session,
        customer_id: int,
    ) -> list[RecoveryMemory]:

        return (
            db.query(RecoveryMemory)
            .filter(
                RecoveryMemory.customer_id == customer_id
            )
            .order_by(
                RecoveryMemory.created_at.desc()
            )
            .all()
        )