from __future__ import annotations

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Drug(Base):
    """Normalized master list of all unique drugs."""

    __tablename__ = "drugs"
    __table_args__ = (
        Index("idx_drugs_generic_name", "generic_name"),
        Index("idx_drugs_aware_group", "aware_group"),
    )

    drug_id: Mapped[str] = mapped_column(String, primary_key=True)
    generic_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    aware_group: Mapped[str | None] = mapped_column(String, nullable=True)
    antibiotic_class: Mapped[str | None] = mapped_column(String, nullable=True)
    route: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="drug",
        passive_deletes=True,
    )
