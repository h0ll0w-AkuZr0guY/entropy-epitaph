"""
Monument router — create, read, maintain, condole.
"""

import random
import asyncio
from datetime import datetime, timezone, timedelta, date

from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Monument, MaintenanceLog, CondoleLog
from backend.schemas import MonumentCreate, MonumentOut, MaintainOut
from backend.session_utils import get_user_id
from backend import entropy_engine as ee
from backend.ai_service import get_ai_service
from backend.wayback_client import check_wayback, format_wayback_date

router = APIRouter(prefix="/monuments", tags=["monuments"])

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
VISUAL_STYLES = ["css", "canvas", "ascii"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _detect_code_metadata(content: str) -> tuple[str, int, int]:
    """Very simple heuristic code metadata extraction."""
    lines = content.splitlines()
    line_count = len(lines)
    comment_count = sum(
        1 for ln in lines
        if ln.strip().startswith(("#", "//", "/*", "*", "--"))
    )
    # crude language detection
    lang = "unknown"
    lowered = content.lower()
    if "def " in content or "import " in content and ":" in content:
        lang = "python"
    if "function" in lowered or "const " in content or "=>" in content:
        lang = "javascript"
    if "public class" in content or "void main" in lowered:
        lang = "java"
    if "#include" in content:
        lang = "c/c++"
    if content.strip().startswith("<?php"):
        lang = "php"
    return lang, line_count, comment_count


def _to_out(m: Monument, cert_id: str | None = None) -> MonumentOut:
    return MonumentOut(
        id=m.id,
        type=m.type,
        title=m.title,
        original_content=m.original_content,
        current_content=m.current_content or m.original_content,
        epitaph=m.epitaph,
        whisper=m.whisper,
        entropy_score=round(m.entropy_score, 4),
        decay_stage=m.decay_stage,
        visual_style=m.visual_style,
        is_public=m.is_public,
        wayback_snapshot_url=m.wayback_snapshot_url,
        wayback_last_seen=m.wayback_last_seen,
        code_language=m.code_language,
        code_lines=m.code_lines,
        random_seed=m.random_seed,
        tilt_angle=ee.tilt_angle(m.random_seed, m.entropy_score),
        created_at=m.created_at,
        last_maintained_at=m.last_maintained_at,
        extinct_at=m.extinct_at,
        cert_id=cert_id,
    )


async def _cert_id_for(db: AsyncSession, monument_id: str) -> str | None:
    """Look up the certificate id for a monument, if any (avoids lazy-load)."""
    from backend.models import ExtinctionCertificate
    result = await db.execute(
        select(ExtinctionCertificate.cert_id).where(
            ExtinctionCertificate.monument_id == monument_id
        )
    )
    return result.scalar_one_or_none()


async def _generate_epitaph_bg(monument_id: str):
    """Background task to generate the epitaph after creation."""
    from backend.database import AsyncSessionLocal
    ai = get_ai_service()
    async with AsyncSessionLocal() as db:
        m = await db.get(Monument, monument_id)
        if not m:
            return
        epitaph = await ai.generate_epitaph(m)
        if m.type == "nameless":
            m.whisper = epitaph
        else:
            m.epitaph = epitaph
        await db.commit()


@router.post("", response_model=MonumentOut)
@router.post("/", response_model=MonumentOut)
async def create_monument(
    payload: MonumentCreate,
    request: Request,
    response: Response,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user_id = get_user_id(request, response)

    # Lock visual style (resolve 'random')
    style = payload.visual_style
    if style == "random":
        style = random.choice(VISUAL_STYLES)

    seed = random.randint(0, 999999)
    now = utcnow()

    m = Monument(
        user_id=user_id,
        type=payload.type,
        title=payload.title,
        original_content=payload.content,
        current_content=payload.content,
        entropy_score=0.0,
        decay_stage=1,
        decay_rate=ee.assign_decay_rate(payload.type),
        last_decay_at=now,
        visual_style=style,
        random_seed=seed,
        is_public=payload.is_public,
        created_at=now,
    )

    # Type-specific preprocessing
    if payload.type == "code" and payload.content:
        lang, lines, comments = _detect_code_metadata(payload.content)
        m.code_language = lang
        m.code_lines = lines
        m.code_comments = comments

    elif payload.type == "link" and payload.content:
        wb = await check_wayback(payload.content.strip())
        if wb["archived"]:
            m.wayback_snapshot_url = wb["snapshot_url"]
            m.wayback_last_seen = format_wayback_date(wb["last_seen"])

    elif payload.type == "nameless":
        m.original_content = None
        m.current_content = None
        m.hour_of_day = now.hour
        m.day_of_week = WEEKDAYS[now.weekday()]

    db.add(m)
    await db.commit()
    await db.refresh(m)

    # Fire-and-forget epitaph generation
    background.add_task(_generate_epitaph_bg, m.id)

    return _to_out(m, cert_id=None)


@router.get("/my", response_model=list[MonumentOut])
async def get_my_monuments(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user_id = get_user_id(request, response)
    result = await db.execute(
        select(Monument)
        .where(Monument.user_id == user_id)
        .order_by(Monument.created_at.desc())
    )
    monuments = result.scalars().all()
    out = []
    for m in monuments:
        cert_id = await _cert_id_for(db, m.id) if m.extinct_at else None
        out.append(_to_out(m, cert_id=cert_id))
    return out


@router.get("/{monument_id}", response_model=MonumentOut)
async def get_monument(
    monument_id: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user_id = get_user_id(request, response)
    m = await db.get(Monument, monument_id)
    if not m or m.user_id != user_id:
        raise HTTPException(404, "此碑不存在，或已彻底消逝。")
    cert_id = await _cert_id_for(db, m.id) if m.extinct_at else None
    return _to_out(m, cert_id=cert_id)


@router.post("/{monument_id}/maintain", response_model=MaintainOut)
async def maintain_monument(
    monument_id: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user_id = get_user_id(request, response)
    m = await db.get(Monument, monument_id)
    if not m:
        raise HTTPException(404, "此碑不存在。")
    if m.user_id != user_id:
        raise HTTPException(403, "你不能擦拭别人的碑。")
    if m.extinct_at is not None:
        raise HTTPException(410, "此碑已寂灭，无法再擦拭。")

    # One maintenance per user per monument per day
    today_str = date.today().isoformat()
    existing = await db.execute(
        select(MaintenanceLog).where(
            MaintenanceLog.user_id == user_id,
            MaintenanceLog.monument_id == monument_id,
        )
    )
    logs = existing.scalars().all()
    for log in logs:
        if log.maintained_at.date().isoformat() == today_str:
            raise HTTPException(429, "今日已擦拭，明日再来。")

    rollback = ee.calculate_maintenance_rollback(m.entropy_score)
    m.entropy_score = max(0.0, m.entropy_score - rollback)
    m.decay_stage = ee.get_decay_stage(m.entropy_score)
    m.last_maintained_at = utcnow()

    db.add(MaintenanceLog(
        user_id=user_id,
        monument_id=monument_id,
        effect=rollback,
        maintained_at=utcnow(),
    ))
    await db.commit()

    next_day = (date.today() + timedelta(days=1))
    return MaintainOut(
        rollback=round(rollback, 6),
        new_entropy=round(m.entropy_score, 4),
        new_stage=m.decay_stage,
        next_maintain_at=next_day.isoformat(),
    )


@router.post("/{monument_id}/condole", status_code=204)
async def condole_monument(
    monument_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Anonymous condolence — extends a public monument's life.
    No feedback is returned (204). Deliberate: a small kindness with no reward.
    """
    m = await db.get(Monument, monument_id)
    if not m or not m.is_public or m.extinct_at is not None:
        # Silent — we don't reveal why nothing happened
        return Response(status_code=204)

    ip = request.client.host if request.client else "unknown"
    today_str = date.today().isoformat()

    # One condole per IP per monument per day
    existing = await db.execute(
        select(CondoleLog).where(
            CondoleLog.monument_id == monument_id,
            CondoleLog.ip_address == ip,
            CondoleLog.condoled_date == today_str,
        )
    )
    if existing.scalar_one_or_none():
        return Response(status_code=204)  # already condoled today, silent

    effect = ee.calculate_condole_effect(m.total_condole_effect)
    if effect > 0:
        m.entropy_score = max(0.0, m.entropy_score - effect)
        m.decay_stage = ee.get_decay_stage(m.entropy_score)
        m.total_condole_effect += effect

    db.add(CondoleLog(
        monument_id=monument_id,
        ip_address=ip,
        condoled_date=today_str,
        effect=effect,
    ))
    await db.commit()
    return Response(status_code=204)
