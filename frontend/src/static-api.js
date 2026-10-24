// Browser-local API adapter used by GitHub Pages.
// It mirrors the FastAPI contract, starts from the canonical showcase fixture,
// and persists visitor actions in localStorage. No remote backend is required.

const STORAGE_KEY = "entropy-epitaph:showcase:v1";
const NOISE_CHARS = "░▒▓│┼╳╬█▀▄";
const STAGE_THRESHOLDS = [0.2, 0.45, 0.7, 0.9];
const RATE_RANGES = {
  code: [0.005, 0.012],
  relic: [0.003, 0.01],
  image: [0.004, 0.011],
  link: [0.008, 0.015],
  nameless: [0.004, 0.011],
};
const FALLBACK_EPITAPHS = {
  code: "此代码生于需求，终于遗忘。它曾运行过，这已足够。",
  relic: "有些话说出来就消失了，没说出来也一样。",
  image: "这张图曾被看过很多遍。像素正在忘记它自己。",
  link: "这个地址曾经指向某处。现在它指向虚空。",
  nameless: null,
};
const FINAL_EPITAPHS = {
  code: "代码停了，风仍在运行。",
  relic: "终于，归于寂静。",
  image: "最后一个像素也熄灭了。",
  link: "地址归零，来处不可考。",
  nameless: "沉默回到沉默。",
};
const CONTENT_TYPES = new Set(["css", "canvas", "ascii"]);

function error(message, status) {
  const value = new Error(message);
  value.status = status;
  return value;
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function getStage(entropy) {
  if (entropy < STAGE_THRESHOLDS[0]) return 1;
  if (entropy < STAGE_THRESHOLDS[1]) return 2;
  if (entropy < STAGE_THRESHOLDS[2]) return 3;
  if (entropy < STAGE_THRESHOLDS[3]) return 4;
  return 5;
}

function tiltAngle(seed, entropy) {
  const direction = seed % 2 === 0 ? 1 : -1;
  return Number((direction * ((seed % 7) + 1) * entropy).toFixed(2));
}

function stringHash(value) {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function deterministicNoise(id, bucket) {
  return (stringHash(`${id}:${bucket}`) % 10000) / 10000;
}

function corruptContent(text, stage, seed) {
  if (!text || stage <= 1) return text;
  const keep = { 2: 0.75, 3: 0.48, 4: 0.1, 5: 0.025 }[stage] ?? 0;
  let output = "";
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (/\s|[，。！？、,.!?;:(){}\[\]<>/\\"'`_\-+=]/u.test(char)) {
      output += char;
      continue;
    }
    const n = deterministicNoise(`${seed}:${i}`, stage);
    output += n <= keep ? char : NOISE_CHARS[stringHash(`${seed}:${i}:noise`) % NOISE_CHARS.length];
  }
  return output;
}

function publicFragment(item) {
  if (item.type === "nameless" || item.type === "image") return null;
  const source = (item.current_content || "").slice(0, 120);
  if (!source) return null;
  const minimumMask = Math.max(0.25, item.entropy_score);
  return [...source].map((char, index) => {
    if (/\s/u.test(char)) return char;
    return deterministicNoise(`${item.random_seed}:public:${index}`, 1701) >= minimumMask ? char : "·";
  }).join("");
}

async function sha256Hex(value) {
  if (globalThis.crypto?.subtle) {
    const bytes = new TextEncoder().encode(value);
    const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("");
  }

  // Deterministic fallback for older test/browser environments.
  let result = "";
  let current = value;
  for (let i = 0; i < 8; i += 1) {
    const hash = stringHash(`${current}:${i}`).toString(16).padStart(8, "0");
    result += hash;
    current = hash + current;
  }
  return result.slice(0, 64);
}

function isoNow(clock) {
  const value = clock();
  return (value instanceof Date ? value : new Date(value)).toISOString();
}

function today(clock) {
  return isoNow(clock).slice(0, 10);
}

function randomInt(max) {
  if (globalThis.crypto?.getRandomValues) {
    const value = new Uint32Array(1);
    globalThis.crypto.getRandomValues(value);
    return value[0] % max;
  }
  return Math.floor(Math.random() * max);
}

function codeMetadata(content) {
  const value = content || "";
  const lower = value.toLowerCase();
  let language = "unknown";
  if (/\bdef\s+\w+|\bimport\s+\w+/.test(value)) language = "python";
  if (/\bfunction\b|\bconst\b|=>/.test(value)) language = "javascript";
  if (/public\s+class|void\s+main/i.test(value)) language = "java";
  if (value.includes("#include")) language = "c/c++";
  if (lower.includes("select ") || lower.includes("alter table")) language = "sql";
  return { language, lines: value ? value.split(/\r?\n/).length : 0 };
}

export function createStaticApi(options = {}) {
  const fixtureUrl =
    options.fixtureUrl || `${import.meta.env.BASE_URL || "/"}mock/showcase.v1.json`;
  const fetchImpl = options.fetchImpl || globalThis.fetch?.bind(globalThis);
  const storage = options.storage || globalThis.localStorage;
  const clock = options.clock || (() => new Date());
  let state = null;
  let fixture = null;

  if (!fetchImpl) throw new Error("Static API requires fetch");

  async function loadFixture() {
    if (fixture) return fixture;
    const response = await fetchImpl(fixtureUrl);
    if (!response.ok) throw error(`演示数据加载失败 (${response.status})`, response.status);
    fixture = await response.json();
    if (!Array.isArray(fixture.monuments) || fixture.monuments.length < 50) {
      throw error("演示数据不完整", 500);
    }
    return fixture;
  }

  function readCached(base) {
    if (!storage) return null;
    try {
      const cached = JSON.parse(storage.getItem(STORAGE_KEY) || "null");
      if (
        cached?.fixtureVersion === base.version &&
        cached?.fixtureSeed === base.seed &&
        Array.isArray(cached.monuments) &&
        Array.isArray(cached.certificates)
      ) {
        return cached;
      }
    } catch (_) {
      // Corrupted browser state is safely replaced by the canonical fixture.
    }
    return null;
  }

  function save() {
    if (!storage || !state) return;
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (reason) {
      console.warn("Could not persist showcase state", reason);
    }
  }

  async function ensureState() {
    if (state) return state;
    const base = await loadFixture();
    state = readCached(base) || {
      fixtureVersion: base.version,
      fixtureSeed: base.seed,
      monuments: deepClone(base.monuments),
      certificates: deepClone(base.certificates),
      demoMode: false,
      lastTick: isoNow(clock),
      maintenance: {},
      condoles: {},
    };
    save();
    return state;
  }

  async function createCertificate(monument, extinctAt) {
    const contentHash = await sha256Hex(monument.original_content || "");
    const payload = `${monument.id}|${extinctAt}|${contentHash.slice(0, 16)}`;
    const fullHash = await sha256Hex(payload);
    const raw = fullHash.slice(0, 12);
    const certId = `EXTINCT-${raw.slice(0, 4)}-${raw.slice(4, 8)}-${raw.slice(8)}`;
    const [low, high] = RATE_RANGES[monument.type] || [0.004, 0.01];
    const certificate = {
      cert_id: certId,
      monument_id: monument.id,
      epitaph_final: FINAL_EPITAPHS[monument.type],
      full_hash: fullHash,
      entropy_score: 0,
      decay_rate: Number((((low + high) / 2) * 3).toFixed(6)),
      last_decay_at: extinctAt,
      extinct_at: null,
      archived: false,
      created_at: extinctAt,
    };
    state.certificates.push(certificate);
    monument.cert_id = certId;
  }

  async function tick() {
    await ensureState();
    const now = new Date(isoNow(clock));
    const last = new Date(state.lastTick || now);
    const elapsedHours = Math.max(0, Math.min(24 * 31, (now - last) / 3600000));
    if (elapsedHours <= 0) return;

    const multiplier = state.demoMode ? 720 : 1;
    const bucket = Math.floor(now.getTime() / (state.demoMode ? 3000 : 30000));

    for (const monument of state.monuments) {
      if (monument.extinct_at) continue;
      const noise = -0.1 + deterministicNoise(monument.id, bucket) * 0.3;
      const previousStage = monument.decay_stage;
      monument.entropy_score = Number(
        Math.min(1, monument.entropy_score + monument.decay_rate * elapsedHours * multiplier * (1 + noise)).toFixed(6),
      );
      monument.decay_stage = getStage(monument.entropy_score);
      monument.tilt_angle = tiltAngle(monument.random_seed, monument.entropy_score);
      monument.last_decay_at = now.toISOString();
      if (monument.decay_stage !== previousStage && monument.original_content) {
        monument.current_content = corruptContent(
          monument.original_content,
          monument.decay_stage,
          monument.random_seed,
        );
      }
      if (monument.entropy_score >= 1) {
        monument.entropy_score = 1;
        monument.decay_stage = 5;
        monument.current_content = null;
        monument.extinct_at = now.toISOString();
        await createCertificate(monument, monument.extinct_at);
      }
    }

    for (const certificate of state.certificates) {
      if (certificate.archived || certificate.extinct_at) continue;
      const noise = -0.1 + deterministicNoise(certificate.cert_id, bucket) * 0.3;
      certificate.entropy_score = Number(
        Math.min(1, certificate.entropy_score + certificate.decay_rate * elapsedHours * multiplier * (1 + noise)).toFixed(6),
      );
      certificate.last_decay_at = now.toISOString();
      if (certificate.entropy_score >= 1) {
        certificate.entropy_score = 1;
        certificate.extinct_at = now.toISOString();
        certificate.archived = true;
      }
    }

    state.lastTick = now.toISOString();
    save();
  }

  async function myMonuments() {
    await tick();
    return deepClone(
      [...state.monuments].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),
    );
  }

  async function getMonument(id) {
    await tick();
    const monument = state.monuments.find((item) => item.id === id);
    if (!monument) throw error("此碑不存在，或已彻底消逝。", 404);
    return deepClone(monument);
  }

  async function createMonument(payload) {
    await tick();
    const now = isoNow(clock);
    const type = payload.type;
    if (!RATE_RANGES[type]) throw error("未知的墓碑类型", 422);

    const isImage = type === "image";
    // Image monuments are always canvas-rendered; the picture is the medium.
    const style = isImage
      ? "canvas"
      : payload.visual_style === "random"
        ? ["css", "canvas", "ascii"][randomInt(3)]
        : payload.visual_style;
    if (!isImage && !CONTENT_TYPES.has(style)) throw error("未知的视觉风格", 422);

    const seed = randomInt(1000000);
    const content = type === "nameless" ? null : payload.content || null;
    const [low, high] = RATE_RANGES[type];
    const metadata = type === "code" ? codeMetadata(content) : { language: null, lines: null };
    const date = new Date(now);
    const monument = {
      id: globalThis.crypto?.randomUUID?.() || `local-${Date.now()}-${seed}`,
      user_id: "browser-local",
      type,
      title: payload.title || null,
      original_content: content,
      current_content: content,
      image_src: isImage ? (payload.image_src || null) : null,
      image_key: isImage ? (payload.image_key || null) : null,
      epitaph: type === "nameless" ? null : FALLBACK_EPITAPHS[type],
      whisper: type === "nameless" ? "此处曾有人驻足。" : null,
      entropy_score: 0,
      decay_stage: 1,
      decay_rate: Number((low + (high - low) * (seed / 1000000)).toFixed(6)),
      last_decay_at: now,
      visual_style: style,
      random_seed: seed,
      tilt_angle: 0,
      is_public: Boolean(payload.is_public),
      wayback_snapshot_url: null,
      wayback_last_seen: null,
      code_language: metadata.language,
      code_lines: metadata.lines,
      code_comments: null,
      hour_of_day: type === "nameless" ? date.getUTCHours() : null,
      day_of_week: type === "nameless" ? date.toLocaleDateString("zh-CN", { weekday: "short", timeZone: "UTC" }) : null,
      created_at: now,
      last_maintained_at: null,
      extinct_at: null,
      total_condole_effect: 0,
      cert_id: null,
    };
    state.monuments.unshift(monument);
    save();
    return deepClone(monument);
  }

  async function maintain(id) {
    await tick();
    const monument = state.monuments.find((item) => item.id === id);
    if (!monument) throw error("此碑不存在。", 404);
    if (monument.extinct_at) throw error("此碑已寂灭，无法再擦拭。", 410);
    const key = `${id}:${today(clock)}`;
    if (state.maintenance[key]) throw error("今日已擦拭，明日再来。", 429);

    const rollback = Number((0.05 * (1 - monument.entropy_score) ** 2).toFixed(6));
    monument.entropy_score = Number(Math.max(0, monument.entropy_score - rollback).toFixed(6));
    monument.decay_stage = getStage(monument.entropy_score);
    monument.tilt_angle = tiltAngle(monument.random_seed, monument.entropy_score);
    monument.last_maintained_at = isoNow(clock);
    state.maintenance[key] = rollback;
    save();
    const tomorrow = new Date(`${today(clock)}T00:00:00.000Z`);
    tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
    return {
      rollback,
      new_entropy: monument.entropy_score,
      new_stage: monument.decay_stage,
      next_maintain_at: tomorrow.toISOString().slice(0, 10),
    };
  }

  async function publicMonuments() {
    await tick();
    return state.monuments
      .filter((item) => item.is_public)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .map((item) => ({
        id: item.id,
        type: item.type,
        current_content: publicFragment(item),
        image_src: item.type === "image" ? item.image_src : null,
        whisper: item.whisper,
        epitaph: item.epitaph,
        entropy_score: item.entropy_score,
        decay_stage: item.decay_stage,
        visual_style: item.visual_style,
        random_seed: item.random_seed,
        tilt_angle: item.tilt_angle,
        created_at: item.created_at,
        extinct_at: item.extinct_at,
        cert_id: item.cert_id,
      }));
  }

  async function condole(id) {
    await tick();
    const monument = state.monuments.find((item) => item.id === id);
    if (!monument || !monument.is_public || monument.extinct_at) return null;
    const key = `${id}:${today(clock)}`;
    if (state.condoles[key]) return null;
    const remaining = Math.max(0, 0.15 - (monument.total_condole_effect || 0));
    const effect = Number(Math.min(0.03, remaining).toFixed(6));
    monument.entropy_score = Number(Math.max(0, monument.entropy_score - effect).toFixed(6));
    monument.decay_stage = getStage(monument.entropy_score);
    monument.total_condole_effect = Number(((monument.total_condole_effect || 0) + effect).toFixed(6));
    monument.tilt_angle = tiltAngle(monument.random_seed, monument.entropy_score);
    state.condoles[key] = effect;
    save();
    return null;
  }

  async function archive() {
    await tick();
    return state.certificates
      .filter((item) => !item.archived)
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      .map((item, index) => ({
        index: index + 1,
        cert_id: item.cert_id,
        created_at: item.created_at,
        entropy_score: item.entropy_score,
      }));
  }

  async function getCertificate(certId) {
    await tick();
    const certificate = state.certificates.find((item) => item.cert_id === certId && !item.archived);
    if (!certificate) throw error("此凭证已不可考。", 404);
    return deepClone(certificate);
  }

  async function resetShowcase() {
    if (storage) storage.removeItem(STORAGE_KEY);
    state = null;
    await ensureState();
    return { reset: true };
  }

  return {
    isStatic: true,
    health: async () => ({ status: "alive", mode: "static-showcase" }),
    createMonument,
    myMonuments,
    getMonument,
    maintain,
    publicMonuments,
    condole,
    archive,
    getCertificate,
    getDemoMode: async () => {
      await ensureState();
      return { demo_mode: state.demoMode };
    },
    toggleDemoMode: async () => {
      await tick();
      state.demoMode = !state.demoMode;
      state.lastTick = isoNow(clock);
      save();
      return { demo_mode: state.demoMode };
    },
    resetShowcase,
    _debugState: async () => {
      await ensureState();
      return state;
    },
  };
}
