from datetime import datetime

from sqlalchemy.orm import Session

from backend.database.models import RecoveryOutcome


def create_recovery_outcome(
    db: Session,
    action_id: int,
    recovered: bool = False,
    recovered_amount: int = 0,
    failure_reason: str | None = None,
    pending: bool = False,
) -> RecoveryOutcome:

    outcome = RecoveryOutcome(
        action_id=action_id,
        outcome=(
            "recovered" if recovered else
            "awaiting_confirmation" if pending else
            "failed"
        ),
        recovered_amount=recovered_amount if recovered else 0,
        failure_reason=failure_reason if not recovered else None,
        # An order/action can be awaiting a customer payment; that is not a
        # verified outcome yet.
        verified_at=datetime.utcnow() if not pending else None,
    )

    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    return outcome
