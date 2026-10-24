"""
Public graveyard router — the anonymous 无名墓区.
"""

import random

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Monument
from backend.schemas import PublicMonumentOut
from backend import entropy_engine as ee

router = APIRouter(prefix="/public", tags=["public"])


def _public_fragment(monument: Monument) -> str | None:
    """Return a stable, partial fragment; never expose pristine original text."""
    if monument.type == "nameless":
        return None
    source = (monument.current_content or "")[:120]
    if not source:
        return None
    rng = random.Random(monument.random_seed + 1701)
    minimum_mask = max(0.25, monument.entropy_score)
    return "".join(
        char if char.isspace() or rng.random() >= minimum_mask else "·"
        for char in source
    )


@router.get("/monuments", response_model=list[PublicMonumentOut])
async def get_public_monuments(db: AsyncSession = Depends(get_db)):
    """
    Returns all public monuments, anonymized.
    Author, title, and original content are hidden —
    only the decayed current state is visible.
    """
    result = await db.execute(
        select(Monument)
        .where(Monument.is_public.is_(True))
        .order_by(Monument.created_at.desc())
    )
    monuments = result.scalars().all()
    return [
        PublicMonumentOut(
            id=m.id,
            type=m.type,
            # Always return a partial, deterministically masked fragment.
            current_content=_public_fragment(m),
            whisper=m.whisper,
            epitaph=m.epitaph,
            entropy_score=round(m.entropy_score, 4),
            decay_stage=m.decay_stage,
            visual_style=m.visual_style,
            random_seed=m.random_seed,
            tilt_angle=ee.tilt_angle(m.random_seed, m.entropy_score),
            created_at=m.created_at,
            extinct_at=m.extinct_at,
        )
        for m in monuments
    ]
