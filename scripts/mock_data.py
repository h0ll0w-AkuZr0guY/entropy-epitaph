#!/usr/bin/env python3
"""CLI for generating, validating, and seeding showcase data.

Examples (run from repository root):
  python scripts/mock_data.py generate --count 120
  python scripts/mock_data.py validate
  python scripts/mock_data.py seed
  python scripts/mock_data.py all --count 120
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.mock_data import (  # noqa: E402
    DEFAULT_AS_OF,
    DEFAULT_COUNT,
    DEFAULT_SEED,
    generate_showcase,
    load_showcase,
    parse_datetime,
    seed_showcase_database,
    validate_showcase,
    write_showcase,
)

DEFAULT_FIXTURE = ROOT / "frontend" / "public" / "mock" / "showcase.v1.json"
DEFAULT_DATABASE = ROOT / "data" / "entropy.db"


def sqlite_url(path: str | Path) -> str:
    resolved = Path(path).resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return "sqlite+aiosqlite:///" + resolved.as_posix()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="熵逝碑林 deterministic showcase data")
    sub = parser.add_subparsers(dest="command", required=True)

    def fixture_arg(cmd: argparse.ArgumentParser) -> None:
        cmd.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)

    def generation_args(cmd: argparse.ArgumentParser) -> None:
        fixture_arg(cmd)
        cmd.add_argument("--count", type=int, default=DEFAULT_COUNT)
        cmd.add_argument("--seed", type=int, default=DEFAULT_SEED)
        cmd.add_argument(
            "--as-of",
            default=DEFAULT_AS_OF.isoformat() + "Z",
            help="Fixed UTC timestamp used for deterministic fixture dates",
        )

    generation_args(sub.add_parser("generate", help="Generate the canonical JSON fixture"))
    fixture_arg(sub.add_parser("validate", help="Validate an existing fixture"))

    seed = sub.add_parser("seed", help="Seed an existing fixture into local SQLite")
    fixture_arg(seed)
    seed.add_argument("--database", type=Path, default=DEFAULT_DATABASE)

    all_cmd = sub.add_parser("all", help="Generate, validate, and seed in one command")
    generation_args(all_cmd)
    all_cmd.add_argument("--database", type=Path, default=DEFAULT_DATABASE)

    return parser.parse_args()


def generate(args: argparse.Namespace) -> dict:
    as_of = parse_datetime(args.as_of)
    if as_of is None:
        raise ValueError("--as-of must be a valid datetime")
    payload = generate_showcase(count=args.count, seed=args.seed, as_of=as_of)
    path = write_showcase(payload, args.fixture)
    print(f"Generated {payload['count']} monuments → {path}")
    print(json.dumps(payload["distribution"], ensure_ascii=False, indent=2))
    return payload


def validate(args: argparse.Namespace) -> dict:
    payload = load_showcase(args.fixture)
    report = validate_showcase(payload)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return payload


async def seed(args: argparse.Namespace, payload: dict | None = None) -> None:
    payload = payload or load_showcase(args.fixture)
    url = sqlite_url(args.database)
    report = await seed_showcase_database(payload, url)
    print(f"Seeded {report['monuments']} monuments and {report['certificates']} certificates")
    print(f"Database → {Path(args.database).resolve()}")


def main() -> int:
    args = parse_args()
    if args.command == "generate":
        generate(args)
    elif args.command == "validate":
        validate(args)
    elif args.command == "seed":
        asyncio.run(seed(args))
    elif args.command == "all":
        payload = generate(args)
        validate_showcase(payload)
        asyncio.run(seed(args, payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
