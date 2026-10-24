import { describe, expect, it } from "vitest";
import fixture from "../public/mock/showcase.v1.json";
import { createStaticApi } from "./static-api.js";

class MemoryStorage {
  constructor() { this.values = new Map(); }
  getItem(key) { return this.values.has(key) ? this.values.get(key) : null; }
  setItem(key, value) { this.values.set(key, String(value)); }
  removeItem(key) { this.values.delete(key); }
}

function harness() {
  const storage = new MemoryStorage();
  let now = new Date("2026-10-24T16:00:00.000Z");
  const fetchImpl = async () => ({
    ok: true,
    status: 200,
    json: async () => structuredClone(fixture),
  });
  const api = createStaticApi({
    fixtureUrl: "fixture.json",
    fetchImpl,
    storage,
    clock: () => new Date(now),
  });
  return {
    api,
    storage,
    fetchImpl,
    clock: () => new Date(now),
    advance(ms) { now = new Date(now.getTime() + ms); },
  };
}

describe("static GitHub Pages API", () => {
  it("loads all 120 balanced showcase monuments", async () => {
    const { api } = harness();
    const monuments = await api.myMonuments();
    expect(monuments).toHaveLength(120);
    expect(new Set(monuments.map((item) => item.type))).toEqual(new Set(["code", "relic", "link", "nameless"]));
    expect(new Set(monuments.map((item) => item.visual_style))).toEqual(new Set(["css", "canvas", "ascii"]));
    expect(new Set(monuments.map((item) => item.decay_stage))).toEqual(new Set([1, 2, 3, 4, 5]));
    expect((await api.publicMonuments()).length).toBe(75);
    expect((await api.archive()).length).toBeGreaterThan(0);
  });

  it("creates and persists a browser-local monument", async () => {
    const h = harness();
    const created = await h.api.createMonument({
      type: "relic",
      content: "这是一条只属于浏览器的告别。",
      visual_style: "ascii",
      is_public: true,
    });
    expect(created.visual_style).toBe("ascii");
    expect(await h.api.myMonuments()).toHaveLength(121);

    const nextApi = createStaticApi({
      fixtureUrl: "fixture.json",
      fetchImpl: h.fetchImpl,
      storage: h.storage,
      clock: h.clock,
    });
    expect(await nextApi.myMonuments()).toHaveLength(121);
    await nextApi.resetShowcase();
    expect(await nextApi.myMonuments()).toHaveLength(120);
  });

  it("allows one maintenance action per UTC day", async () => {
    const { api } = harness();
    const target = (await api.myMonuments()).find((item) => !item.extinct_at);
    const before = target.entropy_score;
    const result = await api.maintain(target.id);
    expect(result.new_entropy).toBeLessThan(before);
    await expect(api.maintain(target.id)).rejects.toMatchObject({ status: 429 });
  });

  it("makes condolence idempotent and respects the lifetime cap", async () => {
    const { api } = harness();
    const target = (await api.publicMonuments()).find(
      (item) => !item.extinct_at && item.entropy_score > 0.1,
    );
    const stateBefore = await api._debugState();
    const original = stateBefore.monuments.find((item) => item.id === target.id).entropy_score;
    await api.condole(target.id);
    const afterFirst = (await api._debugState()).monuments.find((item) => item.id === target.id).entropy_score;
    await api.condole(target.id);
    const afterSecond = (await api._debugState()).monuments.find((item) => item.id === target.id).entropy_score;
    expect(afterFirst).toBeLessThanOrEqual(original);
    expect(afterSecond).toBe(afterFirst);
  });

  it("advances entropy in demo mode and creates extinction certificates", async () => {
    const h = harness();
    const before = await h.api._debugState();
    const certCount = before.certificates.length;
    const previouslyExtinct = new Set(before.monuments.filter((item) => item.extinct_at).map((item) => item.id));
    await h.api.toggleDemoMode();
    h.advance(30_000);
    await h.api.myMonuments();
    const after = await h.api._debugState();
    expect(after.monuments.some((item) => item.extinct_at && !previouslyExtinct.has(item.id))).toBe(true);
    expect(after.certificates.length).toBeGreaterThan(certCount);
  });
});
