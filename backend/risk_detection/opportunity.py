from sqlalchemy.orm import Session

from backend.database.models import RecoveryOpportunity


def create_recovery_opportunity(
    db: Session,
    payment_id: int,
    customer_id: int,
    risk_score: int,
    reason: str,
) -> RecoveryOpportunity | None:
    if risk_score < 50:
        return None

    opportunity = RecoveryOpportunity(
        payment_id=payment_id,
        customer_id=customer_id,
        score=risk_score,
        status="open",
        root_cause=reason,
    )

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    return opportunity