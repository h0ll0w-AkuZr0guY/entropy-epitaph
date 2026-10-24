# 演示数据与 GitHub Pages / Showcase Data & Pages

## 标准数据集

`frontend/public/mock/showcase.v1.json` 是唯一标准 fixture，由固定 seed `20261024` 生成：

| 维度 | 分布 |
|---|---|
| 总数 | 120 |
| 类型 | code 30 / relic 30 / link 30 / nameless 30 |
| 阶段 | 1–5 各 24 |
| 风格 | CSS 40 / Canvas 40 / ASCII 40 |
| 公开 | 75 |
| 已寂灭 | 12 |
| 消逝凭证 | 12（其中部分已归档消失） |

全部内容为合成案例。链接使用 `.invalid` 保留域，不包含真人信息或秘密。

## 常用命令

```powershell
# 生成 + 校验 + 灌入本地 data/entropy.db
.\.venv\Scripts\python.exe scripts\mock_data.py all --count 120 --seed 20261024

# 只校验提交的 fixture
.\.venv\Scripts\python.exe scripts\mock_data.py validate

# 灌入指定数据库
.\.venv\Scripts\python.exe scripts\mock_data.py seed --database data\entropy.db

# 静态 Pages 构建
Set-Location frontend
npm run build:pages
```

生成器接受 50–200。标准 120 条正好覆盖完整笛卡尔组合两次。UUID 使用保留命名空间；seed 重复执行不会产生重复行，也不会删除普通用户记录。灌库时会把 `last_decay_at` 重置为当前时间，避免历史演示日期触发瞬间补算。

## 浏览器状态

Pages 首次访问加载 fixture，之后把新增碑、擦拭、凭吊、熵值和演示模式保存在 `entropy-epitaph:showcase:v1`。墓园页的“重置演示数据”会先确认，再清除本浏览器改动并恢复 120 条基线。

Pages 限制：
- 不调用 OpenAI 或 Wayback；使用预制和 fallback 文案。
- 不存在跨访客共享数据库，操作只对当前浏览器有效。
- 凭吊限制基于浏览器与日期，不是服务端 IP。
- 如需真实多人墓园，应另行部署 FastAPI/PostgreSQL 或 BaaS。

## 自动部署

`.github/workflows/pages.yml` 在 `main` 推送后执行前端单测、以静态模式构建、上传 `frontend/dist` 并部署。项目型 Pages 的 base path 在 workflow 中按仓库名计算。自定义 Pages workflow 的构建/上传/部署方式参考 [GitHub 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

仓库设置需要将 Pages Source 设为 **GitHub Actions**。CI 还会校验 fixture、运行 Python/JavaScript 单测和 Playwright 浏览器测试。

Content was rephrased for compliance with licensing restrictions.
