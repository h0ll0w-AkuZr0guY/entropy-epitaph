# 熵逝碑林 / Entropy Epitaph

> **万物终将风化，连遗忘本身也会被遗忘。**<br>
> **Everything decays. Even the memory of forgetting.**

一座所有事物都会风化的数字墓园。你可以为废弃代码、没说出口的话、失效链接或沉默立碑；碑文、碑体，甚至“曾经存在过”的证明，都会遵循熵增持续崩坏并最终消散。

## 在线演示 / Live Demo

**GitHub Pages：<https://h0ll0w-akuzr0guy.github.io/entropy-epitaph/>**

演示站预置 **120 块**合成墓碑：四类各 30、五阶段各 24、三种风格各 40。Pages 不需要后端；新增碑、擦拭、凭吊和演示模式保存在当前浏览器，可一键重置。

## 核心闭环 / Core Loop

1. **立碑 Erect**：代码碑、遗物碑、链接碑、无名碑。
2. **风化 Decay**：基于真实时间增长，加入随机扰动，无法逆转。
3. **擦拭 Delay**：每天一次，越到后期效果越弱。
4. **寂灭 Vanish**：生成 `EXTINCT-xxxx-xxxx-xxxx` 凭证。
5. **遗忘 Forget**：凭证继续衰变，最终从档案中消失。

视觉风格在立碑时锁定：CSS/SVG 模糊、Canvas 像素噪声、ASCII 字符崩坏。

## 快速开始 / Quick Start

```powershell
# Python 环境
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

# 生成、校验并灌入 120 条演示数据
.\.venv\Scripts\python.exe scripts\mock_data.py all --count 120 --seed 20261024

# 后端（终端 1）
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 前端（终端 2）
Set-Location frontend
npm ci
npm run dev
```

打开 <http://127.0.0.1:5173>；API 文档在 <http://127.0.0.1:8000/docs>。`OPENAI_API_KEY` 留空时自动使用本地 fallback。

### Pages 静态预览

```powershell
Set-Location frontend
npm run build:pages
npm run preview
```

### Docker

```powershell
docker compose up --build
```

## 验证 / Verification

```powershell
.\.venv\Scripts\python.exe scripts\mock_data.py validate
.\.venv\Scripts\python.exe -m pytest backend\tests -v
Set-Location frontend
npm ci
npm run test
npm run build:pages
npm run test:e2e
```

## 文档 / Documentation

- [问题分析 / Problem Analysis](docs/problem-analysis.md)
- [产品介绍 / Product Overview](docs/product-overview.md)
- [产品需求与验收标准 / Requirements](docs/requirements.md)
- [技术架构 / Technical Architecture](docs/technical-architecture.md)
- [演示数据与 Pages / Mock Data & Pages](docs/mock-data-and-pages.md)
- [参赛提交文案 / Submission Copy](docs/submission-copy.md)
- [测试报告 / Test Report](docs/test-report.md)
- [完整产品与技术 Spec](.kiro/specs/entropy-epitaph/spec.md)
- [5 分钟演示剧本](demo-script.md)

## 技术栈 / Stack

Python 3.11+ · FastAPI · SQLAlchemy async · SQLite · APScheduler · OpenAI fallback · Wayback API · Vanilla JS · Vite · Pytest · Vitest · Playwright · GitHub Actions · GitHub Pages

## 双模式边界

本地 FastAPI 模式使用 SQLite、APScheduler、OpenAI/Wayback；Pages 模式使用同一份 fixture 和浏览器 localStorage，没有跨访客共享状态或实时 AI。详见[演示数据与 Pages](docs/mock-data-and-pages.md)。

## Pitch

**所有互联网产品都在做永久保存。我们不做备份，我们做告别。**<br>
**Every internet product promises permanence. We don't do backups. We do goodbyes.**
