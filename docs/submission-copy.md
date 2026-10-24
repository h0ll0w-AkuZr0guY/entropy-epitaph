# 参赛提交文案 / Competition Submission Copy

## 项目名 / Project

**熵逝碑林 / Entropy Epitaph**

## Slogan

**万物终将风化，连遗忘本身也会被遗忘。**<br>
**Everything decays. Even the memory of forgetting.**

## 摘要 / Abstract

熵逝碑林是一座所有事物都会消亡的数字墓园。你可以为废弃代码、结束的关系、失效链接或无法说出的事立碑；碑文、碑体和消逝凭证会按真实时间持续衰变，最终连“它曾存在过”的证据也不再留下。

Entropy Epitaph is a digital graveyard where every artifact, tombstone, and proof of existence must eventually disappear.

## 问题 / Problem

互联网只提供两个极端：永久保存，或瞬间删除。前者让数字遗物无限堆积，后者没有告别过程。我们希望为“结束”设计一种可见、有限、不可逆的体验。

## 方案 / Solution

用户选择四种碑之一，并锁定 CSS、Canvas 或 ASCII 风格。后端熵增引擎按照真实时间和随机扰动推进五个衰变阶段。用户每天只能擦拭一次，陌生人可以无反馈地凭吊公开碑，但所有努力都只能延缓最终寂灭。

## 创新点 / Innovation

- 将“必然丢失”而非“永久保存”写入产品底层规则。
- 内容语义与视觉载体同时损坏，不是简单倒计时。
- 消逝凭证也会死亡，使系统形成完整熵增闭环。
- 凭吊没有点赞数、通知或关系链，只保留不求回报的善意。
- 同一契约支持完整 FastAPI 模式和无需后端的 GitHub Pages 演示模式。

## 技术亮点 / Engineering

- FastAPI + SQLAlchemy async + SQLite + APScheduler。
- OpenAI 覆盖五个生成环节，并提供离线 fallback。
- Wayback Machine 快照查询与超时容错。
- 三套独立前端衰变管线：CSS/SVG、Canvas 像素、ASCII。
- SHA-256 唯一消逝凭证。
- 120 条可复现 fixture，覆盖四类型、五阶段、三风格。
- Pytest、Vitest、Playwright、GitHub Actions 与 Pages 自动部署。

## 5分钟演示 / Demo

落地页提出反永久保存主张 → 浏览 120 块不同阶段的碑 → 创建遗物碑 → 开启 ×720 演示模式 → 擦拭高熵碑 → 见证崩塌和凭证生成 → 在公共墓区无反馈凭吊 → 查看逐渐丢页的档案。

## 收尾 / Closing

**我们不做备份，我们做告别。**<br>
**We don't do backups. We do goodbyes.**

## 团队与未来 / Team & Next Steps

- 团队：`[填写姓名 / 角色]`
- 下一步：加密原文、可配置真实寿命、独立任务队列、多人墓园服务、可访问性和内容安全策略。
