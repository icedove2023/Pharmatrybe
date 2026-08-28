from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Evidence(Base):
    """Stores evidence statements, which may be repeated across diseases."""

    __tablename__ = "evidence"
    __table_args__ = (
        Index("idx_evidence_disease_id", "disease_id"),
        Index("idx_evidence_type", "type"),
    )

    evidence_id: Mapped[str] = mapped_column(String, primary_key=True)
    disease_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("diseases.disease_id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    disease: Mapped["Disease"] = relationship(
        "Disease",
        back_populates="evidence",
        passive_deletes=True,
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="evidence",
        passive_deletes=True,
    )
