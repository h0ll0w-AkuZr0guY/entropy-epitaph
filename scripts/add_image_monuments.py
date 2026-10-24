#!/usr/bin/env python3
"""Inject 图片碑 / image monuments into the showcase fixture.

Image monuments carry an inline SVG data-URI in `image_src`. They decay as a
medium (pixelation + desaturation + noise on canvas), so they need no text
corruption. Idempotent: re-running replaces the previously injected set.

Run: python scripts/add_image_monuments.py
"""

from __future__ import annotations

import json
import urllib.parse
import uuid
from datetime import datetime, timedelta
from pathlib import Path

FIXTURE = Path("frontend/public/mock/showcase.v1.json")
NAMESPACE = uuid.UUID("6403e7d3-9627-47cf-9077-ad77836d98a3")
SHOWCASE_USER = "00000000-0000-4000-8000-000000000120"
AS_OF = datetime(2026, 10, 24, 12, 0, 0)

# SVG sources kept byte-identical in meaning to frontend/src/sample-images.js
SVGS = {
    "sunset": """
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#3a2f3a"/><stop offset="55%" stop-color="#7a5a4a"/>
    <stop offset="75%" stop-color="#b08a5a"/><stop offset="100%" stop-color="#1e1a18"/>
  </linearGradient></defs>
  <rect width="320" height="200" fill="url(#sky)"/>
  <circle cx="160" cy="118" r="34" fill="#d8a860" opacity="0.85"/>
  <rect y="130" width="320" height="70" fill="#1a1512" opacity="0.6"/>
  <rect y="138" width="320" height="4" fill="#c8a060" opacity="0.5"/>
  <rect y="150" width="320" height="3" fill="#a07840" opacity="0.4"/>
</svg>""",
    "room": """
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#242018"/>
  <rect x="0" y="0" width="320" height="130" fill="#2e2a22"/>
  <rect x="40" y="40" width="80" height="60" fill="#1a1714" stroke="#4a4236"/>
  <rect x="46" y="46" width="68" height="48" fill="#3a3024"/>
  <rect x="200" y="30" width="90" height="70" fill="#1a1714" stroke="#4a4236"/>
  <rect x="150" y="150" width="60" height="30" fill="#3a332a"/>
  <line x1="0" y1="130" x2="320" y2="130" stroke="#4a4236" stroke-width="2"/>
</svg>""",
    "portrait": """
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#201d1a"/>
  <ellipse cx="160" cy="92" rx="58" ry="72" fill="#4a4038"/>
  <ellipse cx="160" cy="82" rx="46" ry="56" fill="#6a5c4e"/>
  <circle cx="142" cy="78" r="6" fill="#201d1a"/><circle cx="178" cy="78" r="6" fill="#201d1a"/>
  <path d="M146 104 Q160 114 174 104" stroke="#201d1a" stroke-width="3" fill="none"/>
  <rect y="160" width="320" height="40" fill="#2a251f"/>
</svg>""",
    "screenshot": """
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#16130f"/>
  <rect x="0" y="0" width="320" height="26" fill="#2a251f"/>
  <circle cx="16" cy="13" r="5" fill="#5a5244"/>
  <rect x="30" y="9" width="90" height="8" rx="4" fill="#4a4236"/>
  <rect x="16" y="44" width="150" height="26" rx="8" fill="#3a332a"/>
  <rect x="24" y="52" width="110" height="5" rx="2" fill="#6a6254"/>
  <rect x="154" y="86" width="150" height="40" rx="8" fill="#5a4a38"/>
  <rect x="162" y="94" width="130" height="5" rx="2" fill="#8a7a5a"/>
  <rect x="162" y="106" width="90" height="5" rx="2" fill="#8a7a5a"/>
  <rect x="16" y="140" width="120" height="26" rx="8" fill="#3a332a"/>
  <rect x="24" y="148" width="80" height="5" rx="2" fill="#6a6254"/>
</svg>""",
    "map": """
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">
  <rect width="320" height="200" fill="#1a1d18"/>
  <path d="M0 60 L120 40 L200 90 L320 70" stroke="#3a4036" stroke-width="2" fill="none"/>
  <path d="M40 160 L140 120 L240 170 L320 140" stroke="#3a4036" stroke-width="2" fill="none"/>
  <path d="M90 0 L110 200" stroke="#2e342a" stroke-width="2"/>
  <path d="M220 0 L205 200" stroke="#2e342a" stroke-width="2"/>
  <path d="M160 70 C142 70 130 84 130 100 C130 122 160 146 160 146 C160 146 190 122 190 100 C190 84 178 70 160 70 Z" fill="#a04030"/>
  <circle cx="160" cy="100" r="11" fill="#1a1d18"/>
</svg>""",
}

# (key, title, epitaph, stage, entropy, public)
IMAGE_SPECS = [
    ("sunset", "最后一次一起看的海", "这张图曾被看过很多遍。日落的颜色正在被像素遗忘。", 1, 0.08, True),
    ("portrait", "一张开始模糊的脸", "我记得轮廓，却想不起眼神。像素先替我忘了。", 2, 0.34, True),
    ("screenshot", "删掉前截下的对话", "我把它截了下来，以为能留住。现在连字也认不清了。", 3, 0.58, True),
    ("room", "搬空之后的出租屋", "家具搬走了，光还在；现在连光也在褪色。", 4, 0.82, True),
    ("map", "一个不再存在的地方", "地图上还钉着它，但那里早已什么都没有了。", 2, 0.28, False),
]


def data_uri(svg: str) -> str:
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg.strip())


def stage_tilt(seed: int, entropy: float) -> float:
    direction = 1 if seed % 2 == 0 else -1
    return round(direction * ((seed % 7) + 1) * entropy, 2)


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    # Drop any previously injected image monuments to stay idempotent.
    data["monuments"] = [m for m in data["monuments"] if m.get("type") != "image"]

    base_index = 500  # reserved offset so UUIDs never collide with the core set
    for i, (key, title, epitaph, stage, entropy, public) in enumerate(IMAGE_SPECS):
        mid = str(uuid.uuid5(NAMESPACE, f"image-{base_index + i:03d}"))
        seed = 100000 + i * 7919
        created = AS_OF - timedelta(days=stage * 15 + i * 3, hours=i * 2)
        data["monuments"].append({
            "id": mid,
            "user_id": SHOWCASE_USER,
            "type": "image",
            "title": title,
            "original_content": None,
            "current_content": None,
            "image_src": data_uri(SVGS[key]),
            "image_key": key,
            "epitaph": epitaph,
            "whisper": None,
            "entropy_score": entropy,
            "decay_stage": stage,
            "decay_rate": round(0.004 + i * 0.0012, 6),
            "last_decay_at": AS_OF.isoformat() + "Z",
            "visual_style": "canvas",
            "random_seed": seed,
            "tilt_angle": stage_tilt(seed, entropy),
            "is_public": public,
            "wayback_snapshot_url": None,
            "wayback_last_seen": None,
            "code_language": None,
            "code_lines": None,
            "code_comments": None,
            "hour_of_day": None,
            "day_of_week": None,
            "created_at": created.isoformat() + "Z",
            "last_maintained_at": None,
            "extinct_at": None,
            "total_condole_effect": 0.0,
            "cert_id": None,
        })

    data["count"] = len(data["monuments"])
    # Refresh type distribution for transparency.
    types: dict[str, int] = {}
    for m in data["monuments"]:
        types[m["type"]] = types.get(m["type"], 0) + 1
    data["distribution"]["types"] = dict(sorted(types.items()))

    FIXTURE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Total monuments: {data['count']}")
    print(f"Type distribution: {data['distribution']['types']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
