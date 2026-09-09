from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.disease import Disease


class Diagnostic(Base):
    """Diagnostic statements associated with a disease."""

    __tablename__ = "diagnostics"
    __table_args__ = (
        Index("idx_diagnostics_disease_id", "disease_id"),
    )

    diagnostic_id: Mapped[str] = mapped_column(String, primary_key=True)
    disease_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("diseases.disease_id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    disease: Mapped["Disease"] = relationship(
        "Disease",
        back_populates="diagnostics",
        passive_deletes=True,
    )
