from datetime import datetime

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
        status="executed",
        reason=reason,
        executed_at=datetime.utcnow(),
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    return action
