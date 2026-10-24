// Capture real product screenshots for the pitch deck into docs/assets/.
//
// Usage (from frontend/, with a dev server already running in `pages` mode):
//   1) cd frontend && npx vite --mode pages --host 127.0.0.1 --port 5190
//   2) PW_CHANNEL=msedge node ../scripts/capture_screens.mjs
//
// Produces: evo-text.png, evo-image.png, graveyard-images.png, public.png,
//           landing.png, archive.png — the images embedded by make_pitch_deck.py.
//
// The evolution strips (evo-text / evo-image) require tests/evolution.html,
// which renders the same monument-card + decay-renderer modules the product uses,
// at five fixed entropy levels. Recreate that file if regenerating from scratch.

import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";

const DEV = process.env.DEV_URL || "http://127.0.0.1:5190";
const OUT = "../docs/assets";
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ channel: process.env.PW_CHANNEL || undefined });
const page = await browser.newPage({ viewport: { width: 1320, height: 960 }, deviceScaleFactor: 2 });

async function shot(path, clip) {
  await page.screenshot({ path: `${OUT}/${path}`, clip });
}

await page.goto(DEV + "/#/");
await page.evaluate(() => localStorage.clear());

await page.goto(DEV + "/#/graveyard");
await page.waitForSelector(".monument-card", { timeout: 15000 });
await page.selectOption("#filter-type", "image");
await page.waitForTimeout(1100);
await shot("graveyard-images.png", { x: 0, y: 0, width: 1320, height: 960 });

await page.goto(DEV + "/#/public");
await page.waitForSelector(".monument-card", { timeout: 15000 });
await page.waitForTimeout(1100);
await shot("public.png", { x: 0, y: 0, width: 1320, height: 960 });

await page.goto(DEV + "/#/");
await page.waitForSelector(".slogan-zh");
await page.waitForTimeout(500);
await shot("landing.png", { x: 0, y: 0, width: 1320, height: 820 });

await page.goto(DEV + "/#/archive");
await page.waitForTimeout(800);
await shot("archive.png", { x: 0, y: 0, width: 1320, height: 760 });

await browser.close();
console.log("page screenshots written to docs/assets");
