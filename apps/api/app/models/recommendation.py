from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.disease import Disease
    from app.models.drug import Drug
    from app.models.evidence import Evidence
    from app.models.pathogen import Pathogen


class Recommendation(Base):
    """Detailed treatment recommendations linking diseases, evidence, and drugs."""

    __tablename__ = "recommendations"

    __table_args__ = (
        Index("idx_recommendations_disease_id", "disease_id"),
        Index("idx_recommendations_evidence_id", "evidence_id"),
        Index("idx_recommendations_drug_id", "drug_id"),
        Index("idx_recommendations_population", "population"),
        Index("idx_recommendations_type", "recommendation_type"),
        CheckConstraint(
            "source_page > 0",
            name="chk_recommendations_source_page_positive",
        ),
        CheckConstraint(
            "frequency_interval_hours > 0",
            name="chk_recommendations_frequency_interval_hours_positive",
        ),
        CheckConstraint(
            "frequency_times_per_day > 0",
            name="chk_recommendations_frequency_times_per_day_positive",
        ),
        CheckConstraint(
            "duration_days >= 0",
            name="chk_recommendations_duration_days_non_negative",
        ),
    )

    recommendation_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    disease_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("diseases.disease_id", ondelete="CASCADE"),
        nullable=False,
    )

    evidence_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("evidence.evidence_id", ondelete="SET NULL"),
        nullable=True,
    )

    drug_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("drugs.drug_id", ondelete="RESTRICT"),
        nullable=True,
    )

    recommendation_type: Mapped[str | None] = mapped_column(String, nullable=True)
    population: Mapped[str | None] = mapped_column(String, nullable=True)
    severity: Mapped[str | None] = mapped_column(String, nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    dose_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    dose_value_min: Mapped[Numeric | None] = mapped_column(Numeric, nullable=True)
    dose_value_max: Mapped[Numeric | None] = mapped_column(Numeric, nullable=True)
    dose_unit: Mapped[str | None] = mapped_column(String, nullable=True)

    frequency_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency_interval_hours: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    frequency_times_per_day: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    duration_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    criteria_care_setting: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_allergy: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_pregnancy: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_renal_impairment: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_hepatic_impairment: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_other: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    disease: Mapped["Disease"] = relationship(
        "Disease",
        back_populates="recommendations",
        passive_deletes=True,
    )

    evidence: Mapped["Evidence"] = relationship(
        "Evidence",
        back_populates="recommendations",
        passive_deletes=True,
    )

    drug: Mapped["Drug"] = relationship(
        "Drug",
        back_populates="recommendations",
        passive_deletes=True,
    )

    pathogens: Mapped[list["Pathogen"]] = relationship(
        "Pathogen",
        secondary="recommendation_pathogens",
        back_populates="recommendations",
        passive_deletes=True,
    )