# 熵逝碑林 / Entropy Epitaph — Product & Technical Specification

## Slogan
- 中文：**「万物终将风化，连遗忘本身也会被遗忘。」**
- English: **"Everything decays. Even the memory of forgetting."**

---

## Problem Statement

互联网的默认价值观是永久保存。「熵逝碑林」是一个完全逆向的数字装置：它是一座所有东西都会消亡的墓园——碑文、碑体、甚至"曾经存在过"的证明，都遵循热力学第二定律持续瓦解，直到彻底虚无。

面向两类评审：技术评审看到完整的系统架构和可运行的 MVP；产品/创意评审看到强烈的概念主张和演示效果。

---

## Core Rules (Entropy Loop)

1. **立碑**：可为任何数字"遗物"立墓碑，不限品类。
2. **自然风化**：基于真实时间流逝，碑体和内容自动持续衰变，无法阻止、无法逆转，只能延缓。
3. **维护上限**：每天可对一块碑进行1次"擦拭维护"，小幅回退衰变进度，但越到后期维护效果越弱，最终必然崩坏。
4. **终焉寂灭**：碑体彻底损毁时，生成唯一「消逝凭证」（哈希值+极简文字）；凭证本身同样会慢慢熵增，最终连"它曾经存在过"的证明也消失。

---

## Monument Types

| 类型 | 说明 | 衰变特征 |
|---|---|---|
| 代码碑 (code) | 废弃代码、夭折需求、永不合并的分支 | 变量名先乱码→函数结构错位→注释消失→字符碎片 |
| 遗物碑 (relic) | 没说出口的话、结束的关系、放弃的梦想 | 细节丢失→用词模糊→段落错乱→零星词语 |
| 链接碑 (link) | 已404的网站、失效链接、死掉的博客 | 保留Wayback快照，看着它碎掉 |
| 无名碑 (nameless) | 什么都不填，只立一块空碑 | 纯粹风化、倒塌、消失，全程无文字 |

---

## Decay Stages (5 Stages)

| 阶段 | entropy_score | 内容状态 | 碑体状态 |
|---|---|---|---|
| 崭新期 | 0.0 – 0.20 | 文字锐利清晰，排版完整 | 碑体平整，棱角分明 |
| 风化期 | 0.20 – 0.45 | 个别字词替换、细节丢失，语句开始不通顺 | 边缘噪点、磨损，色泽变暗 |
| 锈蚀期 | 0.45 – 0.70 | 大面积乱码、段落错位，只能辨认零星关键词 | 碑身裂纹、缺角，表面斑驳剥落 |
| 废墟期 | 0.70 – 0.90 | 内容90%变噪点，只剩碎片残影 | 碑体断裂、倾斜，大半埋入"数字尘土" |
| 寂灭期 | 0.90 – 1.0+ | 内容彻底消失 | 碑体倒塌，基座淡去，原地只剩空白 |

---

## Requirements

- **衰变时间**：真实时间 + 加速演示双轨，按钮切换（演示模式 ×720 倍速）；含随机扰动（noise ∈ [-0.1, +0.2]）
- **维护机制**：每日1次擦拭，回退公式 `rollback = 0.05 × (1 - entropy_score)²`
- **视觉风格**：CSS/SVG、Canvas/像素、ASCII 三种风格，立碑时选定或随机，**不可更改**
- **AI 功能**：
  - 立碑时生成墓志铭（四类各有专属 prompt）
  - 阶段跃迁时 AI 生成"语义损坏版"内容
  - 链接碑：Wayback 快照 + AI 摘要"它死前最后说了什么"
  - 无名碑：基于时间元数据生成不超过10字的碑前低语
  - 寂灭时生成凭证上的最终墓前词（不超过20字）
- **墓园体系**：个人墓园 + 公共无名墓区（凭吊机制）+ 消逝档案
- **凭吊**：无鉴权，IP 限制每碑每天1次，总凭吊延寿上限 0.15
- **消逝凭证**：`SHA256(monument_id + extinct_at + content_hash)` 前12位，格式 `EXTINCT-xxxx-xxxx-xxxx`，凭证自身 decay_rate 为普通碑3倍

---

## Technical Stack

| 层 | 技术选型 |
|---|---|
| 后端 | Python 3.11+, FastAPI, SQLAlchemy (async), aiosqlite, Alembic |
| 调度 | APScheduler (AsyncIOScheduler) |
| AI | OpenAI API (GPT-4o-mini), httpx async client |
| 外部API | Wayback Machine availability API |
| 前端 | Vanilla JS + Vite，无框架 |
| 视觉 | CSS animations / Canvas pixel manipulation / Unicode block chars |
| 粒子 | 手写 Canvas 粒子（寂灭动画） |
| 部署 | Docker Compose（一键启动） |
| 测试 | pytest + httpx (后端), vitest + playwright (前端) |

---

## Data Models

### Monument
```python
id: UUID
user_id: str (session-based, no auth required for MVP)
type: enum(code, relic, link, nameless)
title: str | None
original_content: str | None
current_content: str | None   # AI衰变后的当前版本
epitaph: str | None           # AI生成墓志铭
entropy_score: float          # 0.0 ~ 1.0+
decay_stage: int              # 1 ~ 5
decay_rate: float             # 每小时衰变量，含随机化
visual_style: enum(css, canvas, ascii)  # 立碑时锁定
is_public: bool
wayback_snapshot_url: str | None  # 链接碑专用
wayback_last_seen: str | None
created_at: datetime
last_maintained_at: datetime | None
extinct_at: datetime | None
random_seed: int              # 确定性随机（倾斜角度等）
hour_of_day: int | None       # 无名碑元数据
day_of_week: str | None       # 无名碑元数据
code_language: str | None     # 代码碑元数据
code_lines: int | None
```

### ExtinctionCertificate
```python
cert_id: str                  # EXTINCT-xxxx-xxxx-xxxx
monument_id: UUID
epitaph_final: str | None     # AI生成最终墓前词
full_hash: str
entropy_score: float          # 凭证自身也会衰减
decay_rate: float             # 普通碑的3倍
extinct_at: datetime | None   # 凭证本身消失的时间（NULL=还存在）
created_at: datetime
archived: bool                # 软删除（消逝档案丢页用）
```

### MaintenanceLog
```python
id: UUID
user_id: str
monument_id: UUID
maintained_at: datetime
effect: float                 # 实际回退量
```

### AppSettings (key-value)
```python
key: str
value: str
updated_at: datetime
```

---

## API Endpoints

| Method | Path | 说明 |
|---|---|---|
| GET | /health | 健康检查 |
| POST | /monuments | 创建墓碑 |
| GET | /monuments/my | 获取我的所有墓碑 |
| GET | /monuments/{id} | 获取墓碑当前状态 |
| POST | /monuments/{id}/maintain | 擦拭维护 |
| GET | /public/monuments | 公共无名墓区 |
| POST | /monuments/{id}/condole | 凭吊 |
| GET | /certificates | 消逝档案 |
| GET | /certificates/{cert_id} | 单个凭证 |
| POST | /settings/demo-mode | 切换演示模式 |

---

## Decay Math

```python
# 每次调度器触发（真实模式每5分钟，演示模式每30秒）
elapsed_hours = (now - last_decay_at) / 3600
noise = random.uniform(-0.1, 0.2)
delta = decay_rate * elapsed_hours * multiplier * (1 + noise)
entropy_score = min(1.0, entropy_score + delta)

# 维护回退
rollback = 0.05 * (1 - entropy_score) ** 2

# 凭吊延寿
condole_effect = min(0.03, max_condole_remaining)
entropy_score = max(0, entropy_score - condole_effect)
```

---

## AI Prompt Strategy

### 代码碑 — 墓志铭
```
System: 你是一位为代码立碑的数字考古学家，用克制的文学语言记录软件的死亡。
User: 这段代码使用 {language}，共 {lines} 行，创建于 {created_at}，死因：{cause}。
      请生成一段不超过100字的墓志铭，包含：生卒年月、死因（从"需求变更/技术债爆炸/弃坑/被替代"选一）、未竟的使命。
      语气：克制、诗性、不煽情。
```

### 遗物碑 — 墓志铭
```
System: 你是一位为情感遗物立碑的记录者，用最少的字承载最重的重量。
User: 用户写下了这些：{content}
      请生成不超过80字的墓志铭。不要解释，不要劝慰，只记录。
```

### 链接碑 — 最后摘要
```
System: 你是互联网考古学家，为已死亡的网页写最后的墓志铭。
User: 这个页面最后存活于 {last_seen}，最后的内容是：{wayback_content_snippet}
      请用不超过60字写下"它死前最后说了什么"。
```

### 无名碑 — 碑前低语
```
System: 你为沉默立碑。用最少的字，说一句话。
User: 有人在 {day_of_week} {hour_of_day}点，什么都没写，只是立了一块碑。
      请生成不超过10个字的碑前低语。不要问为什么。
```

### 寂灭凭证 — 最终墓前词
```
System: 你为消失本身写最后一句话。
User: 一块{type}碑消失了。它存活了 {days} 天，被擦拭了 {maintenance_count} 次。
      请写一句不超过20字的墓前词。
```

### 衰变文字损坏（阶段跃迁时调用）
```
System: 你是时间本身。你会让文字腐烂，但要保留情绪的骨架。
User: 原文：{original_content}
      当前熵值：{entropy_score}（{stage_name}阶段）
      请返回该熵值下的"损坏版"文字：
      - 风化期(0.2-0.45)：替换20-30%的具体细节词为模糊词，保持语义可读
      - 锈蚀期(0.45-0.7)：替换50%内容，插入 ░▒▓ 字符，段落开始错位
      - 废墟期(0.7-0.9)：只保留10%的原始词语，其余替换为 █▓░╳╬│
      只返回损坏后的文字，不要解释。
```

---

## Visual Style Details

### CSS 风格
- 背景：`#1a1a1a`，文字：`#c8c8c0`，衰变文字：`#5a5a4a`
- entropy → `filter: blur(entropy*3px) contrast(1-entropy*0.3)`
- SVG `feTurbulence` 噪声层叠加，opacity 随 entropy 增大
- 碑体 CSS border，随 entropy 增加 border 从 solid → dashed → dotted

### Canvas 风格
- 文字渲染到 canvas，`getImageData` 随 entropy 比例注入随机像素噪声
- `image-rendering: pixelated` 小分辨率放大，产生像素化效果
- RAF 循环，每帧微量噪声累积

### ASCII 风格
- Unicode block chars 替换字符：`' .:-=+*#%@░▒▓│┼╳╬█▀▄'`
- entropy=0: 原始文字；entropy=0.5: 50% block chars；entropy=1.0: 全部噪声字符
- 字体固定 `Courier New` monospace，颜色随 entropy 从绿色 `#00ff41` 退色到灰色 `#5a5a4a`

---

## Demo Script (5分钟现场演示)

1. **[0:00]** 打开落地页，介绍 Slogan 和核心概念（反常识：不做永久保存）
2. **[0:45]** 创建一块「遗物碑」，输入一段文字，选 ASCII 风格，等待 AI 生成墓志铭
3. **[1:30]** 创建一块「链接碑」，输入一个已知的404链接，展示 Wayback 快照捕获
4. **[2:00]** 切换到「演示模式」，观察碑体快速衰变，展示三个不同阶段的碑
5. **[3:00]** 对高熵值碑执行「擦拭维护」，展示 entropy 微小回退，按钮进入冷却
6. **[3:30]** 让一块碑走完全程，触发崩塌动画，展示消逝凭证（EXTINCT-xxxx-xxxx-xxxx）
7. **[4:00]** 切换到「公共无名墓区」，展示匿名碑，执行凭吊操作（无任何社交反馈）
8. **[4:30]** 展示「消逝档案」，只有编号和时间的空条目，档案本身也在慢慢丢页
9. **[4:50]** 回到落地页收尾：**"我们不做备份，我们做告别。"**
