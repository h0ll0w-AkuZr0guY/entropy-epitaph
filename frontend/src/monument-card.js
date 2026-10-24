// Renders a single monument as a tombstone card with its locked visual style.

import {
  renderASCII,
  renderCSS,
  renderCanvas,
  renderImage,
  STAGE_NAMES,
  STAGE_NAMES_EN,
} from "./decay-renderer.js";

const TYPE_LABELS = {
  code: "代码碑 · Code",
  relic: "遗物碑 · Relic",
  image: "图片碑 · Image",
  link: "链接碑 · Link",
  nameless: "无名碑 · Nameless",
};

export function createMonumentCard(m, options = {}) {
  const { onMaintain, onCondole, publicMode = false } = options;

  const card = document.createElement("div");
  card.className = `monument-card style-${m.visual_style} stage-${m.decay_stage}`;
  card.dataset.id = m.id;
  card.dataset.type = m.type;

  const tilt = m.tilt_angle || 0;
  const sink = (m.decay_stage - 1) * 6; // sink into "dust" as it decays
  card.style.transform = `rotate(${tilt}deg) translateY(${sink}px)`;

  // Extinct → show grave dust + certificate link
  if (m.extinct_at) {
    card.classList.add("extinct");
    card.innerHTML = `
      <div class="grave-dust" title="消逝于 ${fmtDate(m.extinct_at)}">
        <div class="dust-base"></div>
        ${m.cert_id ? `<div class="cert-ref">${m.cert_id}</div>` : ""}
      </div>`;
    return card;
  }

  // Header
  const header = document.createElement("div");
  header.className = "mc-header";
  header.innerHTML = `
    <span class="mc-type">${TYPE_LABELS[m.type] || m.type}</span>
    <span class="mc-stage">${STAGE_NAMES[m.decay_stage - 1]} · ${STAGE_NAMES_EN[m.decay_stage - 1]}</span>`;
  card.appendChild(header);

  // Body — the decaying content
  const body = document.createElement("div");
  body.className = "mc-body";

  const content =
    m.type === "nameless"
      ? m.whisper || "……"
      : m.current_content || m.original_content || m.epitaph || "";

  if (m.type === "image" && m.image_src) {
    // Image monuments are always rendered on canvas — the picture is the medium.
    const canvas = document.createElement("canvas");
    canvas.width = 260;
    canvas.height = 150;
    canvas.className = "mc-canvas mc-image";
    body.appendChild(canvas);
    renderImage(canvas, m.image_src, m.entropy_score, m.random_seed);
    card._canvasRefresh = () => renderImage(canvas, m.image_src, m.entropy_score, m.random_seed);
  } else if (m.visual_style === "canvas") {
    const canvas = document.createElement("canvas");
    canvas.width = 260;
    canvas.height = 120;
    canvas.className = "mc-canvas";
    body.appendChild(canvas);
    renderCanvas(canvas, content, m.entropy_score, m.random_seed);
    card._canvasRefresh = () => renderCanvas(canvas, content, m.entropy_score, m.random_seed);
  } else {
    const textEl = document.createElement("pre");
    textEl.className = "mc-text";
    body.appendChild(textEl);
    if (m.visual_style === "ascii") {
      renderASCII(textEl, content, m.entropy_score, m.random_seed);
    } else {
      textEl.textContent = content;
      renderCSS(textEl, m.entropy_score);
    }
  }
  card.appendChild(body);

  // Epitaph (non-nameless)
  if (m.type !== "nameless" && m.epitaph) {
    const ep = document.createElement("div");
    ep.className = "mc-epitaph";
    ep.textContent = `「${m.epitaph}」`;
    card.appendChild(ep);
  }

  // Footer / actions
  const footer = document.createElement("div");
  footer.className = "mc-footer";

  const meta = document.createElement("span");
  meta.className = "mc-meta";
  meta.textContent = `熵 ${(m.entropy_score * 100).toFixed(1)}%`;
  footer.appendChild(meta);

  if (publicMode && onCondole) {
    const btn = document.createElement("button");
    btn.className = "mc-btn condole";
    btn.textContent = "凭吊";
    btn.onclick = async () => {
      btn.disabled = true;
      try {
        await onCondole(m.id);
      } catch (_) {
        btn.disabled = false;
        return;
      }
      // A small, quiet confirmation: the stone briefly grows clearer.
      // No numbers, no thanks — just the feeling that your gesture landed.
      playCondoleRelief(card, m);
      btn.textContent = "已凭吊";
      btn.classList.add("done");
      setTimeout(() => btn.remove(), 1600);
    };
    footer.appendChild(btn);
  } else if (!publicMode && onMaintain) {
    const btn = document.createElement("button");
    btn.className = "mc-btn maintain";
    btn.textContent = "擦拭";
    btn.onclick = () => onMaintain(m, btn, card);
    footer.appendChild(btn);
  }

  card.appendChild(footer);
  return card;
}

// Condolence feedback: the stone briefly clears, then settles back —
// a quiet, rewardless confirmation that the gesture delayed the decay.
function playCondoleRelief(card, m) {
  card.classList.add("condoled");

  // Soft radial pulse over the card — a visible "it got a little clearer".
  const ripple = document.createElement("div");
  ripple.className = "condole-ripple";
  card.appendChild(ripple);
  setTimeout(() => ripple.remove(), 1500);

  const body = card.querySelector(".mc-body");
  const canvas = body && body.querySelector("canvas");
  const textEl = body && body.querySelector(".mc-text");

  const baseEntropy = m.entropy_score;
  const relieved = Math.max(0, baseEntropy - 0.18);
  const start = performance.now();
  const DURATION = 1400;

  function frame(now) {
    const t = Math.min(1, (now - start) / DURATION);
    // Ease out then ease back: clear quickly, fade back toward the true value.
    const dip = Math.sin(t * Math.PI); // 0 → 1 → 0
    const shown = baseEntropy - (baseEntropy - relieved) * dip;

    if (canvas) {
      if (m.type === "image" && m.image_src) {
        renderImage(canvas, m.image_src, shown, m.random_seed);
      } else {
        renderCanvas(canvas, m.current_content || m.epitaph || "", shown, m.random_seed);
      }
    } else if (textEl) {
      if (m.visual_style === "ascii") {
        renderASCII(textEl, m.current_content || m.epitaph || m.whisper || "", shown, m.random_seed);
      } else {
        renderCSS(textEl, shown);
      }
    }

    if (t < 1) {
      requestAnimationFrame(frame);
    } else {
      card.classList.remove("condoled");
    }
  }
  requestAnimationFrame(frame);
}

// Particle collapse animation when a monument reaches extinction.
export function playCollapse(card, onDone) {
  const rect = card.getBoundingClientRect();
  const canvas = document.createElement("canvas");
  canvas.width = rect.width;
  canvas.height = rect.height;
  canvas.className = "collapse-canvas";
  canvas.style.position = "absolute";
  canvas.style.left = card.offsetLeft + "px";
  canvas.style.top = card.offsetTop + "px";
  card.parentElement.appendChild(canvas);
  card.style.visibility = "hidden";

  const ctx = canvas.getContext("2d");
  const particles = [];
  for (let i = 0; i < 180; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height * 0.6,
      vx: (Math.random() - 0.5) * 1.5,
      vy: Math.random() * 1.2 + 0.3,
      life: 1,
      size: Math.random() * 2 + 1,
    });
  }

  let frame = 0;
  function tick() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let alive = false;
    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.03;
      p.life -= 0.012;
      if (p.life > 0) {
        alive = true;
        ctx.fillStyle = `rgba(180,180,170,${p.life})`;
        ctx.fillRect(p.x, p.y, p.size, p.size);
      }
    }
    frame++;
    if (alive && frame < 160) {
      requestAnimationFrame(tick);
    } else {
      canvas.remove();
      if (onDone) onDone();
    }
  }
  tick();
}

export function fmtDate(iso) {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    return d.toLocaleString("zh-CN", { hour12: false });
  } catch (_) {
    return iso;
  }
}
