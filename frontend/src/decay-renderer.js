// Decay renderers — the visual half of entropy.
// Three locked styles: css, canvas, ascii.
// AI corrupts the semantics; these functions corrupt the medium.

const NOISE_CHARS = ["░", "▒", "▓", "│", "┼", "╳", "╬", "█", "▀", "▄"];

// Seeded PRNG so a monument's corruption pattern is stable per render frame
// but deterministic by seed — keeps the same char "dead" rather than flickering wildly.
function seededRandom(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

// ---------- ASCII style ----------
export function corruptText(str, entropy, seed = 12345) {
  if (!str) return str;
  const rand = seededRandom(seed);
  return str
    .split("")
    .map((c) => {
      if (c === "\n" || c === " ") return c;
      if (rand() < entropy) {
        return NOISE_CHARS[Math.floor(rand() * NOISE_CHARS.length)];
      }
      return c;
    })
    .join("");
}

export function renderASCII(element, text, entropy, seed) {
  element.textContent = corruptText(text || "", entropy, seed);
  // Color fades from phosphor green to dead gray
  const g = Math.round(255 * (1 - entropy));
  const base = Math.round(90 + 60 * (1 - entropy));
  element.style.color =
    entropy < 0.5
      ? `rgb(${Math.round(90 * entropy * 2)}, ${g}, ${Math.round(65 * (1 - entropy))})`
      : `rgb(${base}, ${base}, ${Math.round(base * 0.85)})`;
}

// ---------- CSS style ----------
export function renderCSS(element, entropy) {
  const blur = (entropy * 2.6).toFixed(2);
  const contrast = (1 - entropy * 0.35).toFixed(2);
  element.style.filter = `blur(${blur}px) contrast(${contrast})`;
  element.style.opacity = (1 - entropy * 0.7).toFixed(2);
  element.style.letterSpacing = `${(entropy * 2).toFixed(1)}px`;
}

// ---------- Canvas style ----------
export function renderCanvas(canvas, text, entropy, seed) {
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  // Paint text onto a small offscreen buffer, then scale up for pixelation
  const scale = 1 + Math.floor(entropy * 6); // more pixelation as it decays
  const ow = Math.max(1, Math.floor(W / scale));
  const oh = Math.max(1, Math.floor(H / scale));
  const off = document.createElement("canvas");
  off.width = ow;
  off.height = oh;
  const octx = off.getContext("2d");
  octx.fillStyle = "#1a1a1a";
  octx.fillRect(0, 0, ow, oh);

  const fade = Math.round(200 * (1 - entropy * 0.6));
  octx.fillStyle = `rgb(${fade},${fade},${Math.round(fade * 0.9)})`;
  octx.font = `${Math.max(6, Math.floor(14 / scale))}px 'Courier New', monospace`;
  const lines = wrapText(octx, text || "", ow - 4);
  let y = 10 / scale + 6;
  for (const ln of lines.slice(0, Math.floor(oh / 8))) {
    octx.fillText(ln, 2, y);
    y += 8 / scale + 4;
  }

  // Scale up (blocky)
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(off, 0, 0, ow, oh, 0, 0, W, H);

  // Inject pixel noise proportional to entropy
  if (entropy > 0.02) {
    const img = ctx.getImageData(0, 0, W, H);
    const rand = seededRandom((seed || 1) + Math.floor(Date.now() / 400));
    for (let i = 0; i < img.data.length; i += 4) {
      if (rand() < entropy * 0.5) {
        const v = Math.floor(rand() * 255);
        img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      }
    }
    ctx.putImageData(img, 0, 0);
  }
}

function wrapText(ctx, text, maxWidth) {
  const words = text.split(/(\s+)/);
  const lines = [];
  let line = "";
  for (const w of words) {
    if (w === "\n") {
      lines.push(line);
      line = "";
      continue;
    }
    const test = line + w;
    if (ctx.measureText(test).width > maxWidth && line) {
      lines.push(line);
      line = w.trimStart();
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

// Stage names (match backend)
export const STAGE_NAMES = ["崭新期", "风化期", "锈蚀期", "废墟期", "寂灭期"];
export const STAGE_NAMES_EN = ["Pristine", "Weathering", "Corroding", "Ruins", "Extinction"];
