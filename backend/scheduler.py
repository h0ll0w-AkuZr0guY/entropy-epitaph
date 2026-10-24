"""
Entropy decay scheduler using APScheduler.

Runs a periodic job that:
1. Advances entropy on all living monuments (and certificates)
2. Detects stage transitions → triggers AI decay-content regeneration
3. Detects extinction (entropy >= 1.0) → generates certificates
4. Ages out the 消逝档案 (certificates archive loses pages over time)

Job interval:
- Real mode: every 5 minutes
- Demo mode: every 30 seconds
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from backend.database import AsyncSessionLocal
from backend.models import Monument, ExtinctionCertificate, MaintenanceLog
from backend import entropy_engine as ee
from backend.certificate_generator import generate_certificate
from backend.ai_service import get_ai_service
from backend.settings_store import is_demo_mode

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None
JOB_ID = "entropy_decay"

REAL_INTERVAL_SECONDS = 300   # 5 minutes
DEMO_INTERVAL_SECONDS = 30    # 30 seconds


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def run_decay_cycle():
    """One pass of the entropy engine over all living monuments and certificates."""
    async with AsyncSessionLocal() as db:
        demo = await is_demo_mode(db)
        now = utcnow()

        # --- Monuments ---
        result = await db.execute(
            select(Monument).where(Monument.extinct_at.is_(None))
        )
        monuments = result.scalars().all()
        decay_jobs: list[tuple[str, str, float, int]] = []
        final_epitaph_jobs: list[tuple[str, str, int, int]] = []

        for m in monuments:
            elapsed_hours = (now - m.last_decay_at).total_seconds() / 3600.0
            if elapsed_hours <= 0:
                continue

            old_stage = m.decay_stage
            new_entropy = ee.calculate_decay(
                m.entropy_score, m.decay_rate, elapsed_hours, demo_mode=demo
            )
            m.entropy_score = new_entropy
            m.decay_stage = ee.get_decay_stage(new_entropy)
            m.last_decay_at = now

            # Stage transition → regenerate decayed content after this transaction commits.
            if m.decay_stage != old_stage and m.decay_stage in (2, 3, 4):
                if m.original_content:
                    decay_jobs.append((m.id, m.original_content, new_entropy, m.decay_stage))

            # Extinction
            if new_entropy >= 1.0:
                final_epitaph_jobs.append(await _extinguish_monument(db, m, now))

        await db.commit()

        # Background AI jobs start only after records are visible to a new DB session.
        for args in decay_jobs:
            asyncio.create_task(_regenerate_decay_content(*args))
        for args in final_epitaph_jobs:
            asyncio.create_task(_generate_final_epitaph(*args))

        # --- Certificates (they decay too, 3× faster) ---
        cert_result = await db.execute(
            select(ExtinctionCertificate).where(ExtinctionCertificate.extinct_at.is_(None))
        )
        certs = cert_result.scalars().all()
        for c in certs:
            elapsed_hours = (now - c.last_decay_at).total_seconds() / 3600.0
            if elapsed_hours <= 0:
                continue
            c.entropy_score = ee.calculate_decay(
                c.entropy_score, c.decay_rate, elapsed_hours, demo_mode=demo
            )
            c.last_decay_at = now
            if c.entropy_score >= 1.0:
                # The certificate itself vanishes — archive loses the page
                c.extinct_at = now
                c.archived = True

        await db.commit()


async def _extinguish_monument(db, monument: Monument, now: datetime):
    """Generate an extinction certificate and mark monument extinct."""
    monument.extinct_at = now
    monument.entropy_score = 1.0
    monument.decay_stage = 5

    cert_data = generate_certificate(
        monument.id, now, monument.original_content
    )

    # Count maintenance actions and lifespan for the final epitaph
    mlog = await db.execute(
        select(MaintenanceLog).where(MaintenanceLog.monument_id == monument.id)
    )
    maintenance_count = len(mlog.scalars().all())
    days_alive = max(0, (now - monument.created_at).days)

    cert = ExtinctionCertificate(
        cert_id=cert_data["cert_id"],
        monument_id=monument.id,
        full_hash=cert_data["full_hash"],
        entropy_score=0.0,
        decay_rate=ee.get_cert_decay_rate(monument.type),
        last_decay_at=now,
        created_at=now,
    )
    db.add(cert)

    logger.info(f"Monument {monument.id} extinct → certificate {cert_data['cert_id']}")
    return (cert_data["cert_id"], monument.type, days_alive, maintenance_count)


async def _regenerate_decay_content(monument_id: str, original: str, entropy: float, stage: int):
    """Background task: AI-corrupt the content for a stage transition."""
    try:
        ai = get_ai_service()
        corrupted = await ai.generate_decay_content(original, entropy, stage)
        async with AsyncSessionLocal() as db:
            m = await db.get(Monument, monument_id)
            if m and m.extinct_at is None:
                m.current_content = corrupted
                await db.commit()
    except Exception as e:
        logger.warning(f"Decay content regeneration failed for {monument_id}: {e}")


async def _generate_final_epitaph(cert_id: str, mtype: str, days: int, maint: int):
    """Background task: AI final epitaph for a certificate."""
    try:
        ai = get_ai_service()
        epitaph = await ai.generate_final_epitaph(mtype, days, maint)
        async with AsyncSessionLocal() as db:
            cert = await db.get(ExtinctionCertificate, cert_id)
            if cert:
                cert.epitaph_final = epitaph
                await db.commit()
    except Exception as e:
        logger.warning(f"Final epitaph generation failed for {cert_id}: {e}")


def start_scheduler():
    """Start the APScheduler with the real-mode interval."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        run_decay_cycle,
        trigger=IntervalTrigger(seconds=REAL_INTERVAL_SECONDS),
        id=JOB_ID,
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Entropy scheduler started (real mode)")
    return _scheduler


def reconfigure_interval(demo_mode: bool):
    """Reschedule the decay job interval when demo mode toggles."""
    if _scheduler is None:
        return
    interval = DEMO_INTERVAL_SECONDS if demo_mode else REAL_INTERVAL_SECONDS
    _scheduler.reschedule_job(JOB_ID, trigger=IntervalTrigger(seconds=interval))
    logger.info(f"Scheduler interval → {interval}s (demo_mode={demo_mode})")


def shutdown_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
