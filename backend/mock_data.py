"""Deterministic showcase data for local demos and GitHub Pages.

The canonical fixture contains 120 monuments by default:
4 monument types × 5 decay stages × 3 visual styles × 2 variants.
It is synthetic, reproducible, and never calls OpenAI or Wayback Machine.
"""

from __future__ import annotations

import json
import random
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from itertools import product
from pathlib import Path
from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.certificate_generator import generate_certificate
from backend.entropy_engine import (
    BASE_DECAY_RATES,
    calculate_maintenance_rollback,
    get_cert_decay_rate,
    get_decay_stage,
    tilt_angle,
)
from backend.database import Base
from backend.models import (
    AppSettings,
    CondoleLog,
    ExtinctionCertificate,
    MaintenanceLog,
    Monument,
)

FIXTURE_VERSION = "1.0"
DEFAULT_COUNT = 120
MIN_COUNT = 50
MAX_COUNT = 200
DEFAULT_SEED = 20261024
DEFAULT_AS_OF = datetime(2026, 10, 24, 12, 0, 0)
SHOWCASE_USER_ID = "00000000-0000-4000-8000-000000000120"
SHOWCASE_NAMESPACE = uuid.UUID("6403e7d3-9627-47cf-9077-ad77836d98a3")

MONUMENT_TYPES = ("code", "relic", "link", "nameless")
VISUAL_STYLES = ("css", "canvas", "ascii")
STAGES = (1, 2, 3, 4, 5)
STAGE_NAMES = ("崭新期", "风化期", "锈蚀期", "废墟期", "寂灭期")
STAGE_RANGES = {
    1: (0.03, 0.18),
    2: (0.22, 0.43),
    3: (0.48, 0.68),
    4: (0.73, 0.88),
    5: (0.92, 0.985),
}
NOISE = "░▒▓│┼╳╬█▀▄"

CODE_PROJECTS = (
    "凌晨三点的备份脚本", "从未合并的支付重试分支", "夭折的天气小组件", "永远停在 TODO 的解析器",
    "第二版用户中心迁移", "祖传样式覆盖层", "被容器替代的日志清理器", "只在作者电脑运行的构建器",
    "没有用户的推荐引擎", "被砍掉的暗色模式", "第九次重写的权限系统", "无人敢删的兼容补丁",
    "停在评审中的搜索服务", "未通过法务的导出工具", "周五上线又回滚的缓存层",
)
CODE_LANGUAGES = ("python", "javascript", "typescript", "go", "sql", "css", "java")
CODE_CAUSES = ("需求变更", "技术债爆炸", "弃坑", "被替代")

RELIC_TITLES = (
    "没寄出的凌晨邮件", "放弃学琴的第七年", "最后一次一起看海", "写到一半的辞职信", "删掉前的合照描述",
    "没有兑现的夏天", "再也没人使用的昵称", "搬家时留下的钥匙", "错过的末班车", "一直没按下发送",
    "旧手机里的备忘录", "毕业后失联的群聊", "没能养大的植物", "取消收藏的那首歌", "计划表上的环游世界",
    "没有完成的生日礼物", "雨停前没说的话", "退回抽屉的戒指", "忘记密码的日记", "被清空的购物车",
    "再没打开的游戏存档", "错过报名的比赛", "搬空后的出租屋", "凌晨撤回的消息", "没赶上的告别",
    "从通讯录消失的人", "落灰的跑鞋", "从未打印的照片", "写错地址的明信片", "关机前最后一条草稿",
)
RELIC_LINES = (
    "我以为以后还有很多次，所以那天什么也没说。",
    "原本打算在春天开始，后来春天一次次过去。",
    "我们记得同一片海，却不再记得彼此当时的表情。",
    "字写到一半，勇气先离开了。",
    "照片已经删除，只记得窗外很亮。",
    "那个约定没有破裂，只是再也没人提起。",
    "名字还在输入法里，人已经不在生活里。",
    "钥匙仍能开门，只是那扇门不再属于我。",
    "车尾灯消失后，我才想起该追。",
    "光标闪了很久，最后屏幕先暗下去。",
)

LINK_SITES = (
    ("最后一间个人主页", "https://garden-1999.example.invalid/home", "这里收集主人在旧世纪写下的花名与雨声。"),
    ("停更的独立博客", "https://after-midnight.example.invalid/posts/last", "最后一篇文章说，下周会继续更新。"),
    ("失效的毕业作品", "https://class-of-2014.example.invalid/showcase", "十二个名字曾在这里并排发光。"),
    ("被取消的开源计划", "https://forge.example.invalid/abandoned-project", "README 的最后一行仍写着 roadmap。"),
    ("消失的论坛长帖", "https://bbs.example.invalid/thread/404", "有人问了一个问题，许多人认真回答。"),
    ("过期的线上展览", "https://museum-night.example.invalid/room/7", "展期结束后，房间只剩一个地址。"),
    ("无人续费的播客站", "https://quiet-radio.example.invalid/episode/28", "第 28 期说，我们下个月再见。"),
    ("关闭的社团档案", "https://club-archive.example.invalid/2008", "活动照片的缩略图曾排满三页。"),
    ("失联的旅行地图", "https://slow-train.example.invalid/map", "路线停在北纬 35 度的一座小站。"),
    ("被下线的小游戏", "https://pixel-island.example.invalid/play", "最高分榜最后一次刷新在一个雨夜。"),
)

NAMELESS_WHISPERS = (
    "此处曾有人驻足。", "不必知道是什么。", "沉默也有重量。", "风替它说完了。", "这里没有名字。",
    "有些告别无需文字。", "无人认领的黄昏。", "请让它安静离开。", "来过，然后忘记。", "空白不是没有。",
    "某个故事停在这里。", "别问，碑不会回答。", "只留下一点位置。", "它选择不被讲述。", "今夜没有碑文。",
)


def _utc_naive(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return _utc_naive(value) if isinstance(value, datetime) else None
    text = value.strip().replace("Z", "+00:00")
    return _utc_naive(datetime.fromisoformat(text))


def iso_z(value: datetime | None) -> str | None:
    if value is None:
        return None
    return _utc_naive(value).isoformat(timespec="seconds") + "Z"


def showcase_monument_id(index: int) -> str:
    """Stable fixture UUID, independent of generation seed."""
    return str(uuid.uuid5(SHOWCASE_NAMESPACE, f"monument-{index:03d}"))


def _code_sample(language: str, index: int) -> str:
    samples = {
        "python": f'def abandoned_job_{index}():\n    # TODO: 等需求稳定后重写\n    return "still waiting"',
        "javascript": f'export function forgottenFeature{index}() {{\n  // never shipped\n  return Promise.reject("roadmap changed");\n}}',
        "typescript": f'interface Future{index} {{ hope: boolean }}\nconst future: Future{index} = {{ hope: false }};',
        "go": f'func Mission{index}() error {{\n\t// FIXME: owner left the team\n\treturn errors.New("unfinished")\n}}',
        "sql": f'-- migration {index}: never applied\nALTER TABLE memories ADD COLUMN forever_{index} BOOLEAN DEFAULT FALSE;',
        "css": f'.legacy-panel-{index} {{\n  /* remove after redesign */\n  z-index: 99999;\n  opacity: 0.99;\n}}',
        "java": f'public final class Legacy{index} {{\n  // Deprecated before release\n  void run() {{ throw new UnsupportedOperationException(); }}\n}}',
    }
    return samples[language]


def _scenario(monument_type: str, index: int) -> dict[str, Any]:
    if monument_type == "code":
        title = CODE_PROJECTS[index % len(CODE_PROJECTS)]
        language = CODE_LANGUAGES[index % len(CODE_LANGUAGES)]
        cause = CODE_CAUSES[index % len(CODE_CAUSES)]
        content = _code_sample(language, index + 1)
        return {
            "title": f"{title} · {index + 1:02d}",
            "content": content,
            "epitaph": f"生于第 {index + 1} 次迭代，终于{cause}。它未竟的使命，是等到一个不再变化的需求。",
            "language": language,
            "lines": len(content.splitlines()),
            "comments": sum(1 for line in content.splitlines() if line.strip().startswith(("#", "//", "/*", "--"))),
        }
    if monument_type == "relic":
        title = RELIC_TITLES[index % len(RELIC_TITLES)]
        line = RELIC_LINES[index % len(RELIC_LINES)]
        return {
            "title": title,
            "content": f"{line} 第 {index + 1} 次想起时，细节已经和从前不同。",
            "epitaph": f"这里埋着「{title}」。没有解释，也没有重来。",
        }
    if monument_type == "link":
        title, base_url, snippet = LINK_SITES[index % len(LINK_SITES)]
        url = f"{base_url}?memory={index + 1}"
        return {
            "title": f"{title} · {index + 1:02d}",
            "content": url,
            "epitaph": f"这个地址曾指向一处真实角落。它死前最后说：{snippet}",
            "snapshot": f"https://web.archive.org/web/20{10 + index % 15:02d}0615120000/{url}",
            "last_seen": f"20{10 + index % 15:02d}-06-15",
        }
    whisper = NAMELESS_WHISPERS[index % len(NAMELESS_WHISPERS)]
    return {"title": None, "content": None, "epitaph": None, "whisper": whisper}


def _corrupt(text: str | None, stage: int, seed: int) -> str | None:
    if text is None:
        return None
    if stage == 1:
        return text
    rng = random.Random(seed)
    keep_ratio = {2: 0.75, 3: 0.48, 4: 0.10, 5: 0.025}[stage]
    chars: list[str] = []
    for char in text:
        if char.isspace() or char in "，。！？、,.!?;:(){}[]<>/\\\"'`_-+=":
            chars.append(char)
        elif rng.random() <= keep_ratio:
            chars.append(char)
        else:
            chars.append(NOISE[rng.randrange(len(NOISE))])
    if stage == 2:
        return "".join(chars).replace("第", "某个", 1)
    return "".join(chars)


def _entropy_for(stage: int, rng: random.Random, extinct: bool) -> float:
    if extinct:
        return 1.0
    low, high = STAGE_RANGES[stage]
    return round(rng.uniform(low, high), 4)


def _distribution(monuments: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    return {
        "types": dict(sorted(Counter(m["type"] for m in monuments).items())),
        "stages": dict(sorted(Counter(str(m["decay_stage"]) for m in monuments).items())),
        "styles": dict(sorted(Counter(m["visual_style"] for m in monuments).items())),
        "public": dict(sorted(Counter(str(m["is_public"]).lower() for m in monuments).items())),
        "extinct": dict(sorted(Counter(str(bool(m["extinct_at"])).lower() for m in monuments).items())),
    }


def generate_showcase(
    count: int = DEFAULT_COUNT,
    seed: int = DEFAULT_SEED,
    as_of: datetime = DEFAULT_AS_OF,
) -> dict[str, Any]:
    """Generate a deterministic showcase fixture with 50–200 monuments."""
    if not MIN_COUNT <= count <= MAX_COUNT:
        raise ValueError(f"count must be between {MIN_COUNT} and {MAX_COUNT}")

    as_of = _utc_naive(as_of)
    rng = random.Random(seed)
    combinations = list(product(MONUMENT_TYPES, STAGES, VISUAL_STYLES))
    type_indices = Counter()
    monuments: list[dict[str, Any]] = []
    certificates: list[dict[str, Any]] = []

    for index in range(count):
        variant, combo_index = divmod(index, len(combinations))
        monument_type, stage, style = combinations[combo_index]
        scenario_index = type_indices[monument_type]
        type_indices[monument_type] += 1
        scenario = _scenario(monument_type, scenario_index)

        # In the second full matrix, stage-5 records are already extinct.
        extinct = stage == 5 and variant % 2 == 1
        entropy = _entropy_for(stage, rng, extinct)
        created_at = as_of - timedelta(
            days=stage * 17 + scenario_index * 2 + rng.randint(0, 10),
            hours=rng.randint(0, 23),
        )
        monument_extinct_at = None
        if extinct:
            monument_extinct_at = as_of - timedelta(days=rng.randint(1, 14), hours=rng.randint(0, 20))
            if monument_extinct_at <= created_at:
                monument_extinct_at = created_at + timedelta(days=1)

        low, high = BASE_DECAY_RATES[monument_type]
        decay_rate = round(rng.uniform(low, high), 6)
        random_seed = rng.randint(1, 999999)
        monument_id = showcase_monument_id(index)
        original = scenario.get("content")
        current = None if extinct else _corrupt(original, stage, seed + index * 31)
        is_public = variant == 0 or index % 4 == 0
        maintained_at = None
        if not extinct and index % 5 == 0:
            maintained_at = as_of - timedelta(days=1 + index % 6, hours=index % 12)

        monument: dict[str, Any] = {
            "id": monument_id,
            "user_id": SHOWCASE_USER_ID,
            "type": monument_type,
            "title": scenario.get("title"),
            "original_content": original,
            "current_content": current,
            "epitaph": scenario.get("epitaph"),
            "whisper": scenario.get("whisper") if monument_type == "nameless" else None,
            "entropy_score": entropy,
            "decay_stage": stage,
            "decay_rate": decay_rate,
            "last_decay_at": iso_z(as_of),
            "visual_style": style,
            "random_seed": random_seed,
            "tilt_angle": tilt_angle(random_seed, entropy),
            "is_public": is_public,
            "wayback_snapshot_url": scenario.get("snapshot") if monument_type == "link" else None,
            "wayback_last_seen": scenario.get("last_seen") if monument_type == "link" else None,
            "code_language": scenario.get("language") if monument_type == "code" else None,
            "code_lines": scenario.get("lines") if monument_type == "code" else None,
            "code_comments": scenario.get("comments") if monument_type == "code" else None,
            "hour_of_day": (scenario_index * 3 + 1) % 24 if monument_type == "nameless" else None,
            "day_of_week": ("周一", "周二", "周三", "周四", "周五", "周六", "周日")[scenario_index % 7] if monument_type == "nameless" else None,
            "created_at": iso_z(created_at),
            "last_maintained_at": iso_z(maintained_at),
            "extinct_at": iso_z(monument_extinct_at),
            "total_condole_effect": round(min(0.15, (index % 6) * 0.03), 2),
            "cert_id": None,
        }

        if extinct and monument_extinct_at:
            cert_data = generate_certificate(monument_id, monument_extinct_at, original)
            archived = index % 4 == 0
            cert_entropy = round(rng.uniform(0.08, 0.88), 4)
            cert_extinct_at = as_of - timedelta(hours=rng.randint(1, 48)) if archived else None
            certificate = {
                "cert_id": cert_data["cert_id"],
                "monument_id": monument_id,
                "epitaph_final": ("代码停了，风仍在运行。" if monument_type == "code" else
                                    "地址归零，来处不可考。" if monument_type == "link" else
                                    "终于，归于寂静。"),
                "full_hash": cert_data["full_hash"],
                "entropy_score": 1.0 if archived else cert_entropy,
                "decay_rate": get_cert_decay_rate(monument_type),
                "last_decay_at": iso_z(as_of),
                "extinct_at": iso_z(cert_extinct_at),
                "archived": archived,
                "created_at": iso_z(monument_extinct_at),
            }
            certificates.append(certificate)
            monument["cert_id"] = certificate["cert_id"]

        monuments.append(monument)

    payload = {
        "version": FIXTURE_VERSION,
        "seed": seed,
        "generated_at": iso_z(as_of),
        "showcase_user_id": SHOWCASE_USER_ID,
        "count": len(monuments),
        "description": "Synthetic showcase data. No real people, secrets, or live URLs are included.",
        "distribution": _distribution(monuments),
        "monuments": monuments,
        "certificates": certificates,
    }
    validate_showcase(payload)
    return payload


def validate_showcase(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate fixture integrity and return a compact validation report."""
    monuments = payload.get("monuments", [])
    certificates = payload.get("certificates", [])
    count = payload.get("count")
    errors: list[str] = []

    if count != len(monuments):
        errors.append(f"declared count {count} != monument count {len(monuments)}")
    if not MIN_COUNT <= len(monuments) <= MAX_COUNT:
        errors.append(f"monument count must be between {MIN_COUNT} and {MAX_COUNT}")

    ids = [m.get("id") for m in monuments]
    if len(ids) != len(set(ids)):
        errors.append("monument ids are not unique")

    cert_ids = [c.get("cert_id") for c in certificates]
    if len(cert_ids) != len(set(cert_ids)):
        errors.append("certificate ids are not unique")

    monument_by_id = {m["id"]: m for m in monuments if m.get("id")}
    for required, actual in (
        (set(MONUMENT_TYPES), {m.get("type") for m in monuments}),
        (set(VISUAL_STYLES), {m.get("visual_style") for m in monuments}),
        (set(STAGES), {m.get("decay_stage") for m in monuments}),
    ):
        if not required.issubset(actual):
            errors.append(f"missing coverage: {sorted(required - actual)}")

    for index, m in enumerate(monuments):
        score = float(m.get("entropy_score", -1))
        stage = int(m.get("decay_stage", 0))
        if get_decay_stage(score) != stage:
            errors.append(f"monument {index}: stage {stage} inconsistent with entropy {score}")
        if m.get("extinct_at") and (stage != 5 or score != 1.0 or not m.get("cert_id")):
            errors.append(f"monument {index}: extinct record is inconsistent")
        if m.get("type") == "nameless" and m.get("original_content") is not None:
            errors.append(f"monument {index}: nameless record has original content")

    for cert in certificates:
        monument = monument_by_id.get(cert.get("monument_id"))
        if not monument:
            errors.append(f"certificate {cert.get('cert_id')} has no monument")
            continue
        extinct_at = parse_datetime(monument.get("extinct_at"))
        if not extinct_at:
            errors.append(f"certificate {cert.get('cert_id')} belongs to a living monument")
            continue
        expected = generate_certificate(monument["id"], extinct_at, monument.get("original_content"))
        if cert.get("cert_id") != expected["cert_id"] or cert.get("full_hash") != expected["full_hash"]:
            errors.append(f"certificate {cert.get('cert_id')} hash mismatch")

    # Public subset must still demonstrate every type, stage, and style.
    public = [m for m in monuments if m.get("is_public")]
    for label, required, actual in (
        ("type", set(MONUMENT_TYPES), {m["type"] for m in public}),
        ("style", set(VISUAL_STYLES), {m["visual_style"] for m in public}),
        ("stage", set(STAGES), {m["decay_stage"] for m in public}),
    ):
        if not required.issubset(actual):
            errors.append(f"public records missing {label} coverage")

    if errors:
        raise ValueError("Invalid showcase fixture:\n- " + "\n- ".join(errors))

    return {
        "valid": True,
        "count": len(monuments),
        "certificates": len(certificates),
        "distribution": _distribution(monuments),
    }


def write_showcase(payload: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_showcase(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_showcase(payload)
    return payload


def _model_values(model_data: dict[str, Any]) -> dict[str, Any]:
    """Convert a fixture monument to values accepted by the ORM model."""
    datetime_fields = {"last_decay_at", "created_at", "last_maintained_at", "extinct_at"}
    excluded = {"tilt_angle", "cert_id"}
    values: dict[str, Any] = {}
    for key, value in model_data.items():
        if key in excluded:
            continue
        values[key] = parse_datetime(value) if key in datetime_fields else value
    return values


async def seed_showcase_database(
    payload: dict[str, Any],
    database_url: str,
    seeded_at: datetime | None = None,
) -> dict[str, int]:
    """Idempotently seed only the reserved showcase UUID namespace.

    Existing non-showcase records are never deleted. ``last_decay_at`` is rebased
    to seed time so historical fixture dates do not trigger instant catch-up decay.
    """
    validate_showcase(payload)
    now = _utc_naive(seeded_at or datetime.now(timezone.utc))
    engine = create_async_engine(database_url, connect_args={"check_same_thread": False})
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    active_ids = {m["id"] for m in payload["monuments"]}
    reserved_ids = {showcase_monument_id(i) for i in range(MAX_COUNT)}
    stale_ids = reserved_ids - active_ids

    async with session_factory() as db:
        # Remove stale fixture rows only; user-created rows cannot match these UUIDv5 values.
        if stale_ids:
            await db.execute(delete(ExtinctionCertificate).where(ExtinctionCertificate.monument_id.in_(stale_ids)))
            await db.execute(delete(MaintenanceLog).where(MaintenanceLog.monument_id.in_(stale_ids)))
            await db.execute(delete(CondoleLog).where(CondoleLog.monument_id.in_(stale_ids)))
            await db.execute(delete(Monument).where(Monument.id.in_(stale_ids)))

        for raw in payload["monuments"]:
            values = _model_values(raw)
            values["last_decay_at"] = now
            existing = await db.get(Monument, raw["id"])
            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                db.add(Monument(**values))

        await db.flush()

        fixture_cert_ids = {c["cert_id"] for c in payload["certificates"]}
        if active_ids:
            result = await db.execute(
                delete(ExtinctionCertificate)
                .where(ExtinctionCertificate.monument_id.in_(active_ids))
                .where(ExtinctionCertificate.cert_id.not_in(fixture_cert_ids))
            )

        for raw in payload["certificates"]:
            values = dict(raw)
            for key in ("last_decay_at", "extinct_at", "created_at"):
                values[key] = parse_datetime(values.get(key))
            if values["extinct_at"] is None:
                values["last_decay_at"] = now
            existing = await db.get(ExtinctionCertificate, raw["cert_id"])
            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                db.add(ExtinctionCertificate(**values))

        setting = await db.get(AppSettings, "demo_mode")
        if setting:
            setting.value = "false"
        else:
            db.add(AppSettings(key="demo_mode", value="false", updated_at=now))

        await db.commit()

    await engine.dispose()
    return {"monuments": len(payload["monuments"]), "certificates": len(payload["certificates"])}
