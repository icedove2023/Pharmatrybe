"""Owned patient records and immutable approved-task history events."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PatientRecord(Base):
    """A patient record visible only to the account that initiated it."""

    __tablename__ = "patient_records"
    __table_args__ = (Index("idx_patient_records_owner", "owner_user_id"),)

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    owner_user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False, index=True)
    hospital_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(Text)
    date_of_birth: Mapped[str | None] = mapped_column(Text)
    sex: Mapped[str | None] = mapped_column(Text)
    demographics: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PatientHistoryEvent(Base):
    """An approved clinical task event owned by one initiating account."""

    __tablename__ = "patient_history_events"
    __table_args__ = (
        Index("idx_patient_history_events_owner", "owner_user_id"),
        Index("idx_patient_history_events_patient", "patient_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[str] = mapped_column(Text, ForeignKey("patient_records.id", ondelete="CASCADE"), nullable=False)
    owner_user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)