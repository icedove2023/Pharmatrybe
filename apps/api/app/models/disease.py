from __future__ import annotations

from sqlalchemy import ARRAY, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Disease(Base):
    """Core table for disease definitions."""

    __tablename__ = "diseases"
    __table_args__ = (
        Index("idx_diseases_name", "name"),
    )

    disease_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    chapter_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chapter_title: Mapped[str | None] = mapped_column(String, nullable=True)
    care_level: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_pages: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="disease",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="disease",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    diagnostics: Mapped[list["Diagnostic"]] = relationship(
        "Diagnostic",
        back_populates="disease",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    stewardship: Mapped[list["Stewardship"]] = relationship(
        "Stewardship",
        back_populates="disease",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    monitoring: Mapped[list["Monitoring"]] = relationship(
        "Monitoring",
        back_populates="disease",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    follow_up: Mapped[list["FollowUp"]] = relationship(
        "FollowUp",
        back_populates="disease",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    referral: Mapped[list["Referral"]] = relationship(
        "Referral",
        back_populates="disease",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    pathogens: Mapped[list["Pathogen"]] = relationship(
        "Pathogen",
        secondary="disease_pathogens",
        back_populates="diseases",
        passive_deletes=True,
    )
