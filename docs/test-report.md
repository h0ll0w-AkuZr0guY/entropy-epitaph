# 本地测试报告 / Local Test Report

测试日期：2026-10-24
目标：验证 120 条演示数据、本地 FastAPI、GitHub Pages 静态模式、构建与部署配置。

## 结果摘要

| 检查 | 结果 |
|---|---|
| Fixture 结构与哈希校验 | 通过 |
| 后端 Pytest | **13 passed** |
| 前端 Vitest | **9 passed** |
| Playwright 静态站浏览器冒烟 | **本地 1 passed + 已部署 Pages 1 passed** |
| Pages 子路径生产构建 | 通过 |
| npm dependency audit | **0 vulnerabilities** |
| FastAPI 隔离库联调 | 通过 |
| Docker Compose 配置解析 | 通过 |
| Docker 镜像构建 | 未执行完成：本机 Docker Desktop daemon 未启动 |

## 数据校验

```text
总碑数      120
类型        code/relic/link/nameless 各 30
阶段        1/2/3/4/5 各 24
风格        css/canvas/ascii 各 40
公开碑      75
已寂灭碑    12
凭证        12
```

生成器还验证了 50 和 200 两个允许边界，并拒绝 49 与 201。

## FastAPI 联调

使用隔离 SQLite 和 `SHOWCASE_MODE=true` 启动实际 Uvicorn 进程，结果：

```json
{
  "health": "alive",
  "monuments": 121,
  "public_monuments": 75,
  "archive_entries": 9,
  "maintenance": "200 then 429",
  "created_code_language": "python",
  "public_private_fields": []
}
```

报告中的 121 是第二轮联调在 120 条基线上保留第一轮新建碑后再次执行所得；每轮均验证创建后数量精确增加 1。隔离数据库随后已删除，本地正式 `data/entropy.db` 保持标准 120 条基线。

## Pages 浏览器路径

Playwright 使用本机 Microsoft Edge 执行以下真实页面路径：

1. 打开落地页并校验中英 Slogan；
2. 进入个人墓园，确认 120 条和首屏 36 张卡片；
3. 筛选寂灭期，确认 24 条；
4. 新建 ASCII 遗物碑，确认总数 121；
5. 刷新页面，确认 localStorage 持久化；
6. 进入公共区，确认 75 条匿名碑；
7. 进入档案并确认凭证条目；
8. 确认无 `localhost:8000` 请求、无 4xx 响应、无浏览器 console error。

## Pages 构建检查

使用 `VITE_BASE_PATH=/entropy-epitaph/` 构建后确认：

- HTML 资源地址包含 `/entropy-epitaph/assets/`；
- JS fixture 地址为 `/entropy-epitaph/mock/showcase.v1.json`；
- bundle 不包含 `127.0.0.1:8000`；
- `.nojekyll`、favicon 和 fixture 均进入 `dist`。

## 已部署站点验证

对 `https://h0ll0w-akuzr0guy.github.io/entropy-epitaph/` 再次执行同一套 Playwright 全链路，结果 **1 passed**。在线 fixture 返回 `count: 120`，证明 Pages 发布产物和演示数据均已生效。

## 已知环境限制

`docker compose config --quiet` 通过，但 `docker compose build` 无法连接 `dockerDesktopLinuxEngine`。这是本机 Docker Desktop 未启动，不是 Compose 文件解析或应用测试失败。GitHub Pages 发布不依赖 Docker。
