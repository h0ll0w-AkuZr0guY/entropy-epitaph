// 消逝档案 — the extinction archive. Only indices and times. It loses pages too.

import { fmtDate } from "../monument-card.js";

export async function renderArchive(container, ctx) {
  const { api } = ctx;

  container.innerHTML = `
    <div class="archive-head">
      <h2>消逝档案 · Extinction Archive</h2>
      <p class="archive-sub">
        每一块彻底消失的碑，在此只留一个空条目。<br/>
        随时间推移，这份档案本身也会慢慢丢页——到最后，连"消失过"这件事也会被忘记。
      </p>
    </div>
    <div id="archive-list" class="archive-list"></div>
  `;

  const list = container.querySelector("#archive-list");

  let entries = [];
  try {
    entries = await api.archive();
  } catch (e) {
    list.innerHTML = `<div class="err">无法读取档案：${e.message}</div>`;
    return;
  }

  if (!entries.length) {
    list.innerHTML = `<div class="archive-empty">档案空无一物。还没有东西彻底消逝。</div>`;
    return;
  }

  for (const e of entries) {
    const row = document.createElement("div");
    row.className = "archive-row";
    // Entries fade as their own certificate entropy rises
    row.style.opacity = (1 - e.entropy_score * 0.85).toFixed(2);
    const num = String(e.index).padStart(4, "0");
    row.innerHTML = `
      <span class="ar-index">#${num}</span>
      <span class="ar-cert">${e.cert_id}</span>
      <span class="ar-time">${fmtDate(e.created_at)}</span>`;
    list.appendChild(row);
  }
}
