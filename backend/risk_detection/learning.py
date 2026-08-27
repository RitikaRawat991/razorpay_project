from sqlalchemy.orm import Session

from backend.database.models import (
    RecoveryAction,
    RecoveryMemory,
    RecoveryOpportunity,
    RecoveryOutcome,
)


class RecoveryLearningService:
    """
    Learns from completed recovery attempts.

    Maintains one active customer-level memory for each
    customer + root cause combination.
    """

    def learn_from_outcome(
        self,
        db: Session,
        outcome: RecoveryOutcome,
    ) -> dict:

        # ---------------------------------------------------------
        # 1. Find recovery action
        # ---------------------------------------------------------

        action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.id == outcome.action_id
            )
            .first()
        )

        if action is None:
            return {
                "learned": False,
                "reason": "recovery action not found",
            }

        # ---------------------------------------------------------
        # 2. Find recovery opportunity
        # ---------------------------------------------------------

        opportunity = (
            db.query(RecoveryOpportunity)
            .filter(
                RecoveryOpportunity.id
                == action.opportunity_id
            )
            .first()
        )

        if opportunity is None:
            return {
                "learned": False,
                "reason": "recovery opportunity not found",
            }

        # ---------------------------------------------------------
        # 3. Determine root cause
        # ---------------------------------------------------------

        root_cause = (
            opportunity.root_cause
            or "unknown"
        )

        customer_id = opportunity.customer_id
        payment_id = opportunity.payment_id

        # ---------------------------------------------------------
        # 4. Find the LATEST memory for this
        #    customer + root cause.
        #
        #    This is important because old test data may contain
        #    multiple memory rows for the same combination.
        # ---------------------------------------------------------

        memory = (
            db.query(RecoveryMemory)
            .filter(
                RecoveryMemory.customer_id == customer_id,
                RecoveryMemory.root_cause == root_cause,
            )
            .order_by(
                RecoveryMemory.id.desc()
            )
            .first()
        )

        # ---------------------------------------------------------
        # 5. Determine recovery status
        # ---------------------------------------------------------

        recovery_status = (
            "recovered"
            if outcome.outcome == "recovered"
            else "failed"
        )

        # ---------------------------------------------------------
        # 6. Create memory if none exists
        # ---------------------------------------------------------

        if memory is None:

            memory = RecoveryMemory(
                customer_id=customer_id,
                payment_id=payment_id,
                root_cause=root_cause,
                recovery_status=recovery_status,
                attempts=1,
            )

            db.add(memory)

        # ---------------------------------------------------------
        # 7. Update latest existing memory
        # ---------------------------------------------------------

        else:

            memory.attempts += 1

            memory.payment_id = payment_id

            memory.recovery_status = recovery_status

        # ---------------------------------------------------------
        # 8. Save learning
        # ---------------------------------------------------------

        db.commit()
        db.refresh(memory)

        # ---------------------------------------------------------
        # 9. Return learning result
        # ---------------------------------------------------------

        return {
            "learned": True,
            "memory_id": memory.id,
            "customer_id": memory.customer_id,
            "root_cause": memory.root_cause,
            "recovery_status": memory.recovery_status,
            "attempts": memory.attempts,
        }

    # -------------------------------------------------------------
    # Backward-compatible alias
    # -------------------------------------------------------------

    def learn(
        self,
        db: Session,
        outcome: RecoveryOutcome,
        **kwargs,
    ) -> dict:

        return self.learn_from_outcome(
            db=db,
            outcome=outcome,
        )