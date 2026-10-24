"""
Settings router — demo mode toggle.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas import DemoModeOut
from backend.settings_store import is_demo_mode, set_demo_mode
from backend.scheduler import reconfigure_interval

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/demo-mode", response_model=DemoModeOut)
async def get_demo_mode(db: AsyncSession = Depends(get_db)):
    return DemoModeOut(demo_mode=await is_demo_mode(db))


@router.post("/demo-mode", response_model=DemoModeOut)
async def toggle_demo_mode(db: AsyncSession = Depends(get_db)):
    current = await is_demo_mode(db)
    new_value = not current
    await set_demo_mode(db, new_value)
    reconfigure_interval(new_value)
    return DemoModeOut(demo_mode=new_value)
