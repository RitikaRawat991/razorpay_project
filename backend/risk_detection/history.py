from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database.models import Payment


def get_previous_failure_count(
    db: Session,
    merchant_id: int,
    payment_id: int,
) -> int:
    count = (
        db.query(func.count(Payment.id))
        .filter(
            Payment.merchant_id == merchant_id,
            Payment.status.in_(["failed", "declined"]),
            Payment.id != payment_id,
        )
        .scalar()
    )

    return count or 0