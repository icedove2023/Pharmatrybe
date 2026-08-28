from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Referral(Base):
    """Referral guidance associated with a disease."""

    __tablename__ = "referral"
    __table_args__ = (
        Index("idx_referral_disease_id", "disease_id"),
    )

    referral_id: Mapped[str] = mapped_column(String, primary_key=True)
    disease_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("diseases.disease_id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    disease: Mapped["Disease"] = relationship(
        "Disease",
        back_populates="referral",
        passive_deletes=True,
    )
