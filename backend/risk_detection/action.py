from sqlalchemy.orm import Session

from backend.database.models import RecoveryAction


def create_recovery_action(
    db: Session,
    opportunity_id: int,
    action_type: str,
    reason: str | None = None,
) -> RecoveryAction:

    action = RecoveryAction(
        opportunity_id=opportunity_id,
        action_type=action_type,
        # Creating a record is not executing a recovery.  The executor
        # advances this lifecycle only after the external action succeeds.
        status="pending",
        reason=reason,
        executed_at=None,
        razorpay_order_id=None,
        razorpay_payment_id=None,
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    return action
