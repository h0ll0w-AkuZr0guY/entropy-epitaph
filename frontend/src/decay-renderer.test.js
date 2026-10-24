import { describe, expect, it } from "vitest";
import { corruptText, STAGE_NAMES, STAGE_NAMES_EN } from "./decay-renderer.js";

const NOISE = new Set(["░", "▒", "▓", "│", "┼", "╳", "╬", "█", "▀", "▄"]);

describe("ASCII decay renderer", () => {
  it("preserves pristine text", () => {
    expect(corruptText("万物终将风化", 0, 42)).toBe("万物终将风化");
  });

  it("is deterministic for the same monument seed", () => {
    const first = corruptText("Everything decays.", 0.5, 2026);
    const second = corruptText("Everything decays.", 0.5, 2026);
    expect(first).toBe(second);
  });

  it("replaces every non-space character at total entropy", () => {
    const result = corruptText("碑 文", 1, 7);
    expect(result[1]).toBe(" ");
    expect([...result].filter((char) => char !== " ").every((char) => NOISE.has(char))).toBe(true);
  });

  it("keeps bilingual names for five stages", () => {
    expect(STAGE_NAMES).toHaveLength(5);
    expect(STAGE_NAMES_EN).toHaveLength(5);
    expect(STAGE_NAMES[4]).toBe("寂灭期");
    expect(STAGE_NAMES_EN[4]).toBe("Extinction");
  });
});
