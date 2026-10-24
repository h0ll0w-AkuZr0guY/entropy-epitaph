// Personal graveyard — create monuments, filter the showcase, maintain, witness extinction.

import { createMonumentCard, playCollapse } from "../monument-card.js";
import { SAMPLE_IMAGES, SAMPLE_IMAGE_KEYS } from "../sample-images.js";

const PAGE_SIZE = 36;

const IMAGE_LABELS = {
  sunset: "海与日落",
  room: "空房间",
  portrait: "一张脸",
  screenshot: "聊天截图",
  map: "地图上的点",
};

export async function renderGraveyard(container, ctx) {
  const { api, startPolling } = ctx;
  let demoMode = false;
  let allMonuments = [];
  let visibleCount = PAGE_SIZE;
  const filters = { type: "all", stage: "all", style: "all" };

  try {
    demoMode = (await api.getDemoMode()).demo_mode;
  } catch (_) {}

  container.innerHTML = `
    <div class="gy-head">
      <div>
        <h2>我的墓园 · My Graveyard</h2>
        <div class="data-mode">${api.isStatic ? "GitHub Pages · 浏览器本地演示数据" : "FastAPI · 本地 SQLite 实时数据"}</div>
      </div>
      <button id="demo-toggle" class="demo-btn ${demoMode ? "on" : ""}">
        ${demoMode ? "⏩ 演示模式：开 (×720)" : "▶ 演示模式：关"}
      </button>
    </div>

    <div class="create-box">
      <div class="cb-row">
        <select id="m-type">
          <option value="relic">遗物碑 · Relic</option>
          <option value="code">代码碑 · Code</option>
          <option value="image">图片碑 · Image</option>
          <option value="link">链接碑 · Link</option>
          <option value="nameless">无名碑 · Nameless</option>
        </select>
        <select id="m-style">
          <option value="random">风格：随机 · Random</option>
          <option value="ascii">ASCII</option>
          <option value="canvas">Canvas / 像素</option>
          <option value="css">CSS / 模糊</option>
        </select>
        <label class="cb-public">
          <input type="checkbox" id="m-public" /> 公开立于无名墓区
        </label>
      </div>
      <div id="image-picker" class="image-picker" hidden>
        <span class="ip-hint">选一张要埋葬的影像（示例）：</span>
        <div class="ip-thumbs">
          ${SAMPLE_IMAGE_KEYS.map(
            (k, i) =>
              `<button type="button" class="ip-thumb${i === 0 ? " on" : ""}" data-key="${k}" title="${IMAGE_LABELS[k]}">
                 <img src="${SAMPLE_IMAGES[k]}" alt="${IMAGE_LABELS[k]}" />
                 <span>${IMAGE_LABELS[k]}</span>
               </button>`,
          ).join("")}
        </div>
      </div>
      <textarea id="m-content" placeholder="写下要埋葬的东西……（无名碑可留空）"></textarea>
      <button id="m-create" class="cta-small">立碑 · Erect</button>
    </div>

    <div class="showcase-toolbar">
      <div id="showcase-summary" class="showcase-summary">读取碑林中……</div>
      <div class="showcase-filters">
        <select id="filter-type" aria-label="按类型筛选">
          <option value="all">全部类型</option><option value="code">代码碑</option>
          <option value="relic">遗物碑</option><option value="image">图片碑</option>
          <option value="link">链接碑</option><option value="nameless">无名碑</option>
        </select>
        <select id="filter-stage" aria-label="按阶段筛选">
          <option value="all">全部阶段</option><option value="1">崭新期</option>
          <option value="2">风化期</option><option value="3">锈蚀期</option>
          <option value="4">废墟期</option><option value="5">寂灭期</option>
        </select>
        <select id="filter-style" aria-label="按风格筛选">
          <option value="all">全部风格</option><option value="css">CSS</option>
          <option value="canvas">Canvas</option><option value="ascii">ASCII</option>
        </select>
        ${api.isStatic ? '<button id="reset-showcase" class="quiet-btn">重置演示数据</button>' : ""}
      </div>
    </div>

    <div id="graveyard-grid" class="graveyard-grid"></div>
    <button id="load-more" class="load-more" hidden>继续走入碑林 · Load more</button>
    <div id="gy-empty" class="gy-empty" style="display:none">
      这片墓园还是空的。立下第一块碑，然后看着它慢慢消失。
    </div>
  `;

  const grid = container.querySelector("#graveyard-grid");
  const emptyMsg = container.querySelector("#gy-empty");
  const summary = container.querySelector("#showcase-summary");
  const loadMore = container.querySelector("#load-more");
  const typeSel = container.querySelector("#m-type");
  const contentEl = container.querySelector("#m-content");
  const styleSel = container.querySelector("#m-style");
  const imagePicker = container.querySelector("#image-picker");
  let selectedImageKey = SAMPLE_IMAGE_KEYS[0];

  // Image thumbnail selection
  for (const thumb of imagePicker.querySelectorAll(".ip-thumb")) {
    thumb.onclick = () => {
      selectedImageKey = thumb.dataset.key;
      for (const t of imagePicker.querySelectorAll(".ip-thumb")) t.classList.remove("on");
      thumb.classList.add("on");
    };
  }

  typeSel.onchange = () => {
    const t = typeSel.value;
    const isImage = t === "image";
    imagePicker.hidden = !isImage;
    styleSel.disabled = isImage; // image monuments are always canvas
    contentEl.disabled = t === "nameless" || isImage;
    contentEl.placeholder =
      t === "nameless"
        ? "无名碑无需内容——只留一块空碑。"
        : isImage
          ? "图片碑无需文字——它会作为影像慢慢风化。"
          : t === "link"
            ? "粘贴一个已经死掉的链接……"
            : "写下要埋葬的东西……";
  };

  container.querySelector("#m-create").onclick = async () => {
    const type = typeSel.value;
    const payload = {
      type,
      visual_style: styleSel.value,
      is_public: container.querySelector("#m-public").checked,
      content: contentEl.disabled ? null : contentEl.value || null,
    };
    if (type === "image") {
      payload.image_key = selectedImageKey;
      payload.image_src = SAMPLE_IMAGES[selectedImageKey];
    }
    try {
      await api.createMonument(payload);
      contentEl.value = "";
      filters.type = filters.stage = filters.style = "all";
      for (const select of container.querySelectorAll(".showcase-filters select")) select.value = "all";
      visibleCount = PAGE_SIZE;
      await refresh();
    } catch (e) {
      alert("立碑失败：" + e.message);
    }
  };

  container.querySelector("#demo-toggle").onclick = async (event) => {
    const result = await api.toggleDemoMode();
    demoMode = result.demo_mode;
    event.target.textContent = demoMode ? "⏩ 演示模式：开 (×720)" : "▶ 演示模式：关";
    event.target.classList.toggle("on", demoMode);
    startPolling(refresh, demoMode);
  };

  for (const key of ["type", "stage", "style"]) {
    container.querySelector(`#filter-${key}`).onchange = (event) => {
      filters[key] = event.target.value;
      visibleCount = PAGE_SIZE;
      renderList();
    };
  }

  loadMore.onclick = () => {
    visibleCount += PAGE_SIZE;
    renderList();
  };

  const reset = container.querySelector("#reset-showcase");
  if (reset) {
    reset.onclick = async () => {
      if (!confirm("这会清除本浏览器新增的碑和维护记录，并恢复初始演示数据。继续吗？")) return;
      await api.resetShowcase();
      visibleCount = PAGE_SIZE;
      await refresh();
    };
  }

  const knownState = new Map();

  function filteredMonuments() {
    return allMonuments.filter((monument) =>
      (filters.type === "all" || monument.type === filters.type) &&
      (filters.stage === "all" || monument.decay_stage === Number(filters.stage)) &&
      (filters.style === "all" || monument.visual_style === filters.style),
    );
  }

  function renderList() {
    const filtered = filteredMonuments();
    const shown = filtered.slice(0, visibleCount);
    const extinctCount = allMonuments.filter((item) => item.extinct_at).length;
    const publicCount = allMonuments.filter((item) => item.is_public).length;
    summary.textContent = `共 ${allMonuments.length} 块碑 · 公开 ${publicCount} · 已寂灭 ${extinctCount} · 当前筛选 ${filtered.length}`;
    emptyMsg.style.display = allMonuments.length ? "none" : "block";
    loadMore.hidden = shown.length >= filtered.length;
    loadMore.textContent = `继续走入碑林（尚有 ${filtered.length - shown.length} 块）`;

    const freshlyExtinct = [];
    for (const monument of allMonuments) {
      const previous = knownState.get(monument.id);
      if (monument.extinct_at && previous && !previous.extinct) freshlyExtinct.push(monument.id);
      knownState.set(monument.id, { extinct: Boolean(monument.extinct_at) });
    }

    grid.innerHTML = "";
    for (const monument of shown) {
      const card = createMonumentCard(monument, { onMaintain: handleMaintain, publicMode: false });
      grid.appendChild(card);
      if (freshlyExtinct.includes(monument.id)) {
        card.style.visibility = "hidden";
        playCollapse(card, () => { card.style.visibility = "visible"; });
      }
    }
    for (const card of grid.querySelectorAll(".style-canvas")) {
      if (card._canvasRefresh) card._canvasRefresh();
    }
  }

  async function refresh() {
    try {
      allMonuments = await api.myMonuments();
      renderList();
    } catch (e) {
      grid.innerHTML = `<div class="err">无法连接墓园：${e.message}</div>`;
    }
  }

  async function handleMaintain(monument, button, card) {
    try {
      await api.maintain(monument.id);
      card.classList.add("wiping");
      setTimeout(() => card.classList.remove("wiping"), 1800);
      button.disabled = true;
      button.textContent = "已擦拭 · 明日再来";
      await refresh();
    } catch (e) {
      if (e.status === 429) {
        button.disabled = true;
        button.textContent = "今日已擦拭";
      } else {
        alert("擦拭失败：" + e.message);
      }
    }
  }

  await refresh();
  startPolling(refresh, demoMode);
}
