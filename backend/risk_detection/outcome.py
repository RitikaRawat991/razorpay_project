from datetime import datetime

from sqlalchemy.orm import Session

from backend.database.models import RecoveryOutcome


def create_recovery_outcome(
    db: Session,
    action_id: int,
    recovered: bool,
    recovered_amount: int,
    failure_reason: str | None = None,
) -> RecoveryOutcome:

    outcome = RecoveryOutcome(
        action_id=action_id,
        outcome="recovered" if recovered else "failed",
        recovered_amount=recovered_amount if recovered else 0,
        failure_reason=failure_reason if not recovered else None,
        verified_at=datetime.utcnow(),
    )

    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    return outcome