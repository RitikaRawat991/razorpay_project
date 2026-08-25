from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class RecoveryOutcome(Base):
    __tablename__ = "recovery_outcomes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    action_id: Mapped[int] = mapped_column(
        ForeignKey("recovery_actions.id"),
        nullable=False,
        index=True,
    )

    outcome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    recovered_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )