from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FollowUp(Base):
    """Follow-up guidance associated with a disease."""

    __tablename__ = "follow_up"
    __table_args__ = (
        Index("idx_follow_up_disease_id", "disease_id"),
    )

    follow_up_id: Mapped[str] = mapped_column(String, primary_key=True)
    disease_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("diseases.disease_id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    disease: Mapped["Disease"] = relationship(
        "Disease",
        back_populates="follow_up",
        passive_deletes=True,
    )
