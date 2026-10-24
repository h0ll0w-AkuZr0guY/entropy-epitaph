"""
熵逝碑林 / Entropy Epitaph — FastAPI application entrypoint.
"""

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from backend.database import init_db
from backend.ai_service import init_ai_service
from backend.scheduler import start_scheduler, shutdown_scheduler
from backend.routers import monuments, public, certificates, settings as settings_router


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    init_ai_service(os.getenv("OPENAI_API_KEY", ""))
    scheduler_enabled = env_flag("ENABLE_SCHEDULER", True)
    if scheduler_enabled:
        start_scheduler()
    logger.info("熵逝碑林 backend is alive. Everything starts decaying now.")
    yield
    # Shutdown
    if scheduler_enabled:
        shutdown_scheduler()


app = FastAPI(
    title="熵逝碑林 / Entropy Epitaph",
    description="一座所有事物都会风化的数字墓园。Everything decays.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — configurable for local Vite or a separately hosted frontend.
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monuments.router)
app.include_router(public.router)
app.include_router(certificates.router)
app.include_router(settings_router.router)


@app.get("/health")
async def health():
    return {"status": "alive", "project": "熵逝碑林 / Entropy Epitaph"}
