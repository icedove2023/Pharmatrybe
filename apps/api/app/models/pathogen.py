from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.disease import Disease
    from app.models.recommendation import Recommendation


class Pathogen(Base):
    """Normalized master list of all unique pathogens."""

    __tablename__ = "pathogens"

    pathogen_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    diseases: Mapped[list["Disease"]] = relationship(
        "Disease",
        secondary="disease_pathogens",
        back_populates="pathogens",
        passive_deletes=True,
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        secondary="recommendation_pathogens",
        back_populates="pathogens",
        passive_deletes=True,
    )
