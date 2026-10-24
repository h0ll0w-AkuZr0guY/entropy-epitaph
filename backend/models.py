"""
SQLAlchemy ORM models for 熵逝碑林 / Entropy Epitaph.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    String, Float, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def new_uuid() -> str:
    return str(uuid.uuid4())


class Monument(Base):
    """A tombstone erected for any dead digital thing."""
    __tablename__ = "monuments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Monument classification
    type: Mapped[str] = mapped_column(
        SAEnum("code", "relic", "link", "nameless", name="monument_type"),
        nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Content — original is stored as-is; current_content is the AI-decayed version
    original_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI-generated text
    epitaph: Mapped[str | None] = mapped_column(Text, nullable=True)
    whisper: Mapped[str | None] = mapped_column(String(50), nullable=True)  # nameless碑前低语

    # Entropy state
    entropy_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    decay_stage: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    decay_rate: Mapped[float] = mapped_column(Float, nullable=False)  # per hour, randomized at creation
    last_decay_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    # Visual style — immutable after creation
    visual_style: Mapped[str] = mapped_column(
        SAEnum("css", "canvas", "ascii", name="visual_style_type"),
        nullable=False
    )

    # Deterministic randomness (tilt angle, etc.)
    random_seed: Mapped[int] = mapped_column(Integer, nullable=False)

    # Public / private
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Link monument fields
    wayback_snapshot_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    wayback_last_seen: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Code monument metadata
    code_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    code_lines: Mapped[int | None] = mapped_column(Integer, nullable=True)
    code_comments: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Nameless monument metadata (for AI whisper generation)
    hour_of_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day_of_week: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    last_maintained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    extinct_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Total condole effect received (capped at 0.15)
    total_condole_effect: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(
        "MaintenanceLog", back_populates="monument", cascade="all, delete-orphan"
    )
    certificate: Mapped["ExtinctionCertificate | None"] = relationship(
        "ExtinctionCertificate", back_populates="monument", uselist=False
    )


class ExtinctionCertificate(Base):
    """
    The final proof of a monument's existence — itself subject to entropy.
    Format: EXTINCT-xxxx-xxxx-xxxx
    """
    __tablename__ = "extinction_certificates"

    cert_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    monument_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("monuments.id"), nullable=False, unique=True
    )

    # AI-generated final epitaph (≤20 chars)
    epitaph_final: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Cryptographic identity
    full_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # The certificate itself also decays
    entropy_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    decay_rate: Mapped[float] = mapped_column(Float, nullable=False)  # 3× normal rate
    last_decay_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    # When the certificate itself vanishes (soft delete)
    extinct_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    monument: Mapped["Monument"] = relationship("Monument", back_populates="certificate")


class MaintenanceLog(Base):
    """Records each 'wiping' action performed on a monument."""
    __tablename__ = "maintenance_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    monument_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("monuments.id"), nullable=False
    )
    maintained_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    effect: Mapped[float] = mapped_column(Float, nullable=False)  # actual rollback amount

    monument: Mapped["Monument"] = relationship("Monument", back_populates="maintenance_logs")


class AppSettings(Base):
    """Key-value store for application-wide settings (e.g. demo_mode)."""
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class CondoleLog(Base):
    """Tracks condolence actions — IP + monument per day, to enforce rate limits."""
    __tablename__ = "condole_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    monument_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False)
    condoled_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    effect: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
