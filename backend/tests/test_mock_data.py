"""Tests for deterministic showcase generation and SQLite seeding."""

from datetime import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.mock_data import (
    SHOWCASE_USER_ID,
    generate_showcase,
    load_showcase,
    seed_showcase_database,
    validate_showcase,
)
from backend.models import ExtinctionCertificate, Monument
from backend.schemas import CertificateOut, MonumentOut, PublicMonumentOut


def test_default_showcase_is_deterministic_and_balanced():
    first = generate_showcase(count=120, seed=20261024)
    second = generate_showcase(count=120, seed=20261024)
    assert first == second

    assert first["count"] == 120
    assert first["distribution"]["types"] == {
        "code": 30,
        "link": 30,
        "nameless": 30,
        "relic": 30,
    }
    assert first["distribution"]["stages"] == {str(stage): 24 for stage in range(1, 6)}
    assert first["distribution"]["styles"] == {"ascii": 40, "canvas": 40, "css": 40}
    assert len(first["certificates"]) == 12
    assert sum(bool(item["extinct_at"]) for item in first["monuments"]) == 12


def test_showcase_supports_requested_range_and_rejects_outliers():
    assert generate_showcase(count=50)["count"] == 50
    assert generate_showcase(count=200)["count"] == 200
    with pytest.raises(ValueError):
        generate_showcase(count=49)
    with pytest.raises(ValueError):
        generate_showcase(count=201)


def test_fixture_matches_api_contract():
    payload = load_showcase("frontend/public/mock/showcase.v1.json")
    report = validate_showcase(payload)
    assert report["valid"] is True

    for item in payload["monuments"]:
        MonumentOut.model_validate(item)
        PublicMonumentOut.model_validate({
            key: item[key]
            for key in (
                "id", "type", "current_content", "whisper", "epitaph",
                "entropy_score", "decay_stage", "visual_style", "random_seed",
                "tilt_angle", "created_at", "extinct_at",
            )
        })
    for item in payload["certificates"]:
        CertificateOut.model_validate(item)


@pytest.mark.asyncio
async def test_sqlite_seed_is_idempotent(tmp_path):
    payload = generate_showcase(count=120, seed=20261024)
    db_path = tmp_path / "showcase.db"
    database_url = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    seeded_at = datetime(2026, 10, 24, 15, 30, 0)

    await seed_showcase_database(payload, database_url, seeded_at=seeded_at)
    await seed_showcase_database(payload, database_url, seeded_at=seeded_at)

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        monument_count = await session.scalar(select(func.count()).select_from(Monument))
        certificate_count = await session.scalar(select(func.count()).select_from(ExtinctionCertificate))
        showcase_count = await session.scalar(
            select(func.count()).select_from(Monument).where(Monument.user_id == SHOWCASE_USER_ID)
        )
        sample = await session.get(Monument, payload["monuments"][0]["id"])

    await engine.dispose()
    assert monument_count == 120
    assert showcase_count == 120
    assert certificate_count == 12
    assert sample is not None
    assert sample.last_decay_at == seeded_at
