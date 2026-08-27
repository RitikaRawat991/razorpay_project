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

        # Check whether this customer already has
        # memory for the same root cause.
        memory = (
            db.query(RecoveryMemory)
            .filter(
                RecoveryMemory.customer_id == customer_id,
                RecoveryMemory.root_cause == root_cause,
            )
            .order_by(
                RecoveryMemory.created_at.desc()
            )
            .first()
        )

        # If memory already exists, reuse it.
        if memory is not None:
            memory.payment_id = payment_id
            db.commit()
            db.refresh(memory)

            return memory

        # Otherwise create the first memory record.
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