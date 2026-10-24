#!/usr/bin/env python3
"""Live API smoke test for a locally running showcase backend.

Run against an isolated, seeded database. This script intentionally creates one
record and performs one maintenance action.
"""

from __future__ import annotations

import argparse
import json

import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8010")
    parser.add_argument("--expected-monuments", type=int, default=120)
    args = parser.parse_args()

    with httpx.Client(base_url=args.base_url, timeout=10) as client:
        health = client.get("/health")
        health.raise_for_status()

        monuments = client.get("/monuments/my").json()
        public = client.get("/public/monuments").json()
        archive = client.get("/certificates").json()
        assert len(monuments) == args.expected_monuments, len(monuments)
        assert len(public) == 75, len(public)
        assert len(archive) > 0

        target = next(item for item in monuments if not item["extinct_at"])
        maintained = client.post(f"/monuments/{target['id']}/maintain")
        assert maintained.status_code == 200, maintained.text
        repeated = client.post(f"/monuments/{target['id']}/maintain")
        assert repeated.status_code == 429, repeated.text

        created_response = client.post(
            "/monuments",
            json={
                "type": "code",
                "content": "def never_merged():\n    return 'goodbye'",
                "visual_style": "ascii",
                "is_public": False,
            },
        )
        assert created_response.status_code == 200, created_response.text
        created = created_response.json()
        assert created["code_language"] == "python"
        assert created["visual_style"] == "ascii"
        assert len(client.get("/monuments/my").json()) == args.expected_monuments + 1

        forbidden = {"user_id", "title", "original_content"}
        leaked = [sorted(forbidden.intersection(item)) for item in public]
        assert all(not fields for fields in leaked), leaked

    report = {
        "health": "alive",
        "monuments": len(monuments),
        "public_monuments": len(public),
        "archive_entries": len(archive),
        "maintenance": "200 then 429",
        "created_code_language": created["code_language"],
        "public_private_fields": [],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
