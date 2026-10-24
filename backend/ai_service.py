"""
AI Service — wraps OpenAI API calls for all monument AI features.

Features:
- Epitaph generation (4 monument types)
- Decay content corruption (stage transitions)
- Link monument summary from Wayback content
- Nameless monument whisper
- Final extinction epitaph

All calls are async. Fallback text is returned if the API is unavailable.
"""

import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Fallback text for when AI is unavailable (ensures demo works offline)
FALLBACK_EPITAPHS = {
    "code": "此代码生于需求，终于遗忘。它曾运行过，这已足够。",
    "relic": "有些话说出来就消失了，没说出来也一样。",
    "link": "这个地址曾经指向某处。现在它指向虚空。",
    "nameless": "。",
}

FALLBACK_DECAY = {
    2: "某些细节已经……模糊了。那些字，那些词，开始变得不那么确定。",
    3: "░░░ 大部分已经 ▒▒▒ 消失 ░░░ 只剩 ╳╳╳ 碎片 ▓▓▓",
    4: "█▓░╳╬│█▓░╳╬│ ███ ░░░ ╬╬╬ █▓░",
    5: "█████████████████████████████████",
}

FALLBACK_WHISPER = "此处曾有人驻足。"
FALLBACK_FINAL = "终于，归于寂静。"


class AIService:
    """Async AI service backed by OpenAI GPT-4o-mini."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._client = None

    def _get_client(self):
        if not self.api_key:
            return None
        if self._client is None:
            try:
                import openai
                self._client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("openai package not available")
                return None
        return self._client

    async def _call(self, system: str, user: str, max_tokens: int = 200) -> str | None:
        """Make an OpenAI chat completion call. Returns None on failure."""
        client = self._get_client()
        if not client:
            return None
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=max_tokens,
                temperature=0.8,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}")
            return None

    async def generate_epitaph(self, monument) -> str:
        """Generate an epitaph for a newly created monument."""
        monument_type = monument.type

        if monument_type == "code":
            system = "你是一位为代码立碑的数字考古学家，用克制的文学语言记录软件的死亡。"
            lang = monument.code_language or "未知语言"
            lines = monument.code_lines or 0
            created = monument.created_at.strftime("%Y年%m月") if monument.created_at else "未知时间"
            user = (
                f"这段代码使用 {lang}，共 {lines} 行，创建于 {created}。\n"
                f"请生成一段不超过100字的墓志铭，包含：生卒年月、"
                f"死因（从「需求变更/技术债爆炸/弃坑/被替代」选一）、未竟的使命。\n"
                f"语气：克制、诗性、不煽情。只输出墓志铭文字本身。"
            )
            result = await self._call(system, user, max_tokens=150)
            return result or FALLBACK_EPITAPHS["code"]

        elif monument_type == "relic":
            system = "你是一位为情感遗物立碑的记录者，用最少的字承载最重的重量。"
            content = (monument.original_content or "")[:500]
            user = (
                f"用户写下了这些：{content}\n"
                f"请生成不超过80字的墓志铭。不要解释，不要劝慰，只记录。"
                f"只输出墓志铭文字本身。"
            )
            result = await self._call(system, user, max_tokens=120)
            return result or FALLBACK_EPITAPHS["relic"]

        elif monument_type == "link":
            system = "你是互联网考古学家，为已死亡的网页写最后的墓志铭。"
            last_seen = monument.wayback_last_seen or "未知时间"
            content_snippet = (monument.original_content or monument.title or "（无法获取内容）")[:300]
            user = (
                f"这个页面最后存活于 {last_seen}，最后的内容是：{content_snippet}\n"
                f"请用不超过60字写下「它死前最后说了什么」。只输出文字本身。"
            )
            result = await self._call(system, user, max_tokens=100)
            return result or FALLBACK_EPITAPHS["link"]

        elif monument_type == "nameless":
            return await self.generate_nameless_whisper(
                monument.hour_of_day or 0,
                monument.day_of_week or "某天",
            )

        return FALLBACK_EPITAPHS.get(monument_type, "此碑无言。")

    async def generate_decay_content(
        self,
        original_content: str,
        entropy_score: float,
        stage: int,
    ) -> str:
        """Generate semantically corrupted content for a decay stage transition."""
        if not original_content:
            return original_content or ""

        stage_name = ["崭新期", "风化期", "锈蚀期", "废墟期", "寂灭期"][stage - 1]
        system = "你是时间本身。你会让文字腐烂，但要保留情绪的骨架。"
        user = (
            f"原文：{original_content[:600]}\n"
            f"当前熵值：{entropy_score:.2f}（{stage_name}阶段）\n"
            f"请返回该熵值下的「损坏版」文字：\n"
            f"- 风化期(0.2-0.45)：替换20-30%的具体细节词为模糊词，保持语义可读\n"
            f"- 锈蚀期(0.45-0.7)：替换50%内容，插入 ░▒▓ 字符，段落开始错位\n"
            f"- 废墟期(0.7-0.9)：只保留10%的原始词语，其余替换为 █▓░╳╬│\n"
            f"只返回损坏后的文字，不要解释。"
        )
        result = await self._call(system, user, max_tokens=300)
        return result or FALLBACK_DECAY.get(stage, original_content)

    async def generate_nameless_whisper(self, hour: int, day_of_week: str) -> str:
        """Generate a ≤10 char whisper for a nameless monument."""
        system = "你为沉默立碑。用最少的字，说一句话。"
        user = (
            f"有人在 {day_of_week} {hour}点，什么都没写，只是立了一块碑。\n"
            f"请生成不超过10个字的碑前低语。不要问为什么。只输出文字本身。"
        )
        result = await self._call(system, user, max_tokens=30)
        return result or FALLBACK_WHISPER

    async def generate_final_epitaph(
        self,
        monument_type: str,
        days_alive: int,
        maintenance_count: int,
    ) -> str:
        """Generate the final ≤20 char epitaph on the extinction certificate."""
        type_names = {
            "code": "代码",
            "relic": "遗物",
            "link": "链接",
            "nameless": "无名",
        }
        type_name = type_names.get(monument_type, "")
        system = "你为消失本身写最后一句话。"
        user = (
            f"一块{type_name}碑消失了。它存活了 {days_alive} 天，"
            f"被擦拭了 {maintenance_count} 次。\n"
            f"请写一句不超过20字的墓前词。只输出文字本身。"
        )
        result = await self._call(system, user, max_tokens=40)
        return result or FALLBACK_FINAL


# Singleton instance — initialized in main.py with the API key
_ai_service: AIService | None = None


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


def init_ai_service(api_key: str) -> AIService:
    global _ai_service
    _ai_service = AIService(api_key=api_key)
    return _ai_service
