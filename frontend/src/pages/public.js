// Public anonymous graveyard — 无名墓区. Condole for strangers, expect nothing back.

import { createMonumentCard } from "../monument-card.js";

const PAGE_SIZE = 36;

export async function renderPublic(container, ctx) {
  const { api, startPolling } = ctx;
  let demoMode = false;
  let monuments = [];
  let visibleCount = PAGE_SIZE;
  let stageFilter = "all";

  try {
    demoMode = (await api.getDemoMode()).demo_mode;
  } catch (_) {}

  container.innerHTML = `
    <div class="public-head">
      <div>
        <h2>无名墓区 · The Nameless Grounds</h2>
        <p class="public-sub">你看不到作者，看不到完整内容。只能上前凭吊，为它多争取一点点存续。</p>
      </div>
      <select id="public-stage-filter" class="dark-select" aria-label="按阶段筛选">
        <option value="all">全部阶段</option><option value="1">崭新期</option>
        <option value="2">风化期</option><option value="3">锈蚀期</option>
        <option value="4">废墟期</option><option value="5">寂灭期</option>
      </select>
    </div>
    <div id="public-summary" class="showcase-summary"></div>
    <div id="public-grid" class="graveyard-grid public"></div>
    <button id="public-more" class="load-more" hidden>继续向前</button>
    <div id="pub-empty" class="gy-empty" style="display:none">这片公共墓区还没有人立碑。</div>
    <div class="whisper-corner">你不会认识他，他也不会知道你。</div>
  `;

  const grid = container.querySelector("#public-grid");
  const summary = container.querySelector("#public-summary");
  const emptyMsg = container.querySelector("#pub-empty");
  const more = container.querySelector("#public-more");

  container.querySelector("#public-stage-filter").onchange = (event) => {
    stageFilter = event.target.value;
    visibleCount = PAGE_SIZE;
    renderList();
  };
  more.onclick = () => {
    visibleCount += PAGE_SIZE;
    renderList();
  };

  function renderList() {
    const filtered = monuments.filter((item) => stageFilter === "all" || item.decay_stage === Number(stageFilter));
    const shown = filtered.slice(0, visibleCount);
    summary.textContent = `${monuments.length} 块匿名碑 · 当前可见 ${filtered.length}`;
    emptyMsg.style.display = monuments.length ? "none" : "block";
    more.hidden = shown.length >= filtered.length;
    more.textContent = `继续向前（尚有 ${filtered.length - shown.length} 块）`;
    grid.innerHTML = "";

    for (const monument of shown) {
      const card = createMonumentCard(monument, {
        publicMode: true,
        onCondole: async (id) => {
          try {
            await api.condole(id);
          } catch (_) {
            // No status or reward is shown, but a failed request may be tried later.
            throw _;
          }
        },
      });
      grid.appendChild(card);
    }
    for (const card of grid.querySelectorAll(".style-canvas")) {
      if (card._canvasRefresh) card._canvasRefresh();
    }
  }

  async function refresh() {
    try {
      monuments = await api.publicMonuments();
      renderList();
    } catch (e) {
      grid.innerHTML = `<div class="err">无法连接：${e.message}</div>`;
    }
  }

  await refresh();
  startPolling(refresh, demoMode);
}
