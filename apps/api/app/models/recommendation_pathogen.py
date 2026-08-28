from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RecommendationPathogen(Base):
    """Association table linking recommendations to pathogens."""

    __tablename__ = "recommendation_pathogens"

    recommendation_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("recommendations.recommendation_id", ondelete="CASCADE"),
        primary_key=True,
    )
    pathogen_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("pathogens.pathogen_id", ondelete="CASCADE"),
        primary_key=True,
    )
