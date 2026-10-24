"""
Application settings store — key/value persistence in the DB.
Primary use: demo_mode toggle.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import AppSettings

DEMO_MODE_KEY = "demo_mode"


async def get_setting(db: AsyncSession, key: str, default: str = "") -> str:
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    row = result.scalar_one_or_none()
    return row.value if row else default


async def set_setting(db: AsyncSession, key: str, value: str) -> None:
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = value
    else:
        db.add(AppSettings(key=key, value=value))
    await db.commit()


async def is_demo_mode(db: AsyncSession) -> bool:
    val = await get_setting(db, DEMO_MODE_KEY, "false")
    return val.lower() == "true"


async def set_demo_mode(db: AsyncSession, enabled: bool) -> None:
    await set_setting(db, DEMO_MODE_KEY, "true" if enabled else "false")
