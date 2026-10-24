"""
Pydantic schemas for request/response bodies.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class MonumentCreate(BaseModel):
    type: Literal["code", "relic", "link", "nameless"]
    title: str | None = Field(None, max_length=200)
    content: str | None = None
    is_public: bool = False
    visual_style: Literal["css", "canvas", "ascii", "random"] = "random"


class MonumentOut(BaseModel):
    id: str
    type: str
    title: str | None
    original_content: str | None
    current_content: str | None
    epitaph: str | None
    whisper: str | None
    entropy_score: float
    decay_stage: int
    visual_style: str
    is_public: bool
    wayback_snapshot_url: str | None
    wayback_last_seen: str | None
    code_language: str | None
    code_lines: int | None
    random_seed: int
    tilt_angle: float
    created_at: datetime
    last_maintained_at: datetime | None
    extinct_at: datetime | None
    cert_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PublicMonumentOut(BaseModel):
    """Anonymized view for the public graveyard — hides author & original content."""
    id: str
    type: str
    current_content: str | None
    whisper: str | None
    epitaph: str | None
    entropy_score: float
    decay_stage: int
    visual_style: str
    random_seed: int
    tilt_angle: float
    created_at: datetime
    extinct_at: datetime | None


class MaintainOut(BaseModel):
    rollback: float
    new_entropy: float
    new_stage: int
    next_maintain_at: str


class CertificateOut(BaseModel):
    cert_id: str
    monument_id: str
    epitaph_final: str | None
    full_hash: str
    entropy_score: float
    extinct_at: datetime | None
    created_at: datetime
    archived: bool

    model_config = ConfigDict(from_attributes=True)


class ArchiveEntryOut(BaseModel):
    """Minimal archive entry — only an index number and extinction time."""
    index: int
    cert_id: str
    created_at: datetime
    entropy_score: float


class DemoModeOut(BaseModel):
    demo_mode: bool
