from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DiseasePathogen(Base):
    """Association table linking diseases to pathogens."""

    __tablename__ = "disease_pathogens"

    disease_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("diseases.disease_id", ondelete="CASCADE"),
        primary_key=True,
    )
    pathogen_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("pathogens.pathogen_id", ondelete="CASCADE"),
        primary_key=True,
    )
