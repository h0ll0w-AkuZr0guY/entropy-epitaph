import { expect, test } from "@playwright/test";

test("static Pages showcase works without a backend", async ({ page }) => {
  const failedRequests = [];
  const failedResponses = [];
  const consoleErrors = [];
  page.on("requestfailed", (request) => failedRequests.push(`${request.url()} :: ${request.failure()?.errorText}`));
  page.on("response", (response) => {
    if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`);
  });
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto("./#/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.locator(".slogan-zh")).toContainText("万物终将风化");

  await page.goto("./#/graveyard");
  await expect(page.locator("#showcase-summary")).toContainText("共 125 块碑");
  await expect(page.locator(".monument-card")).toHaveCount(36);

  // Image monuments render as canvas pictures.
  await page.selectOption("#filter-type", "image");
  await expect(page.locator("#showcase-summary")).toContainText("当前筛选 5");
  await expect(page.locator('.monument-card[data-type="image"] canvas.mc-image')).toHaveCount(5);
  await page.selectOption("#filter-type", "all");

  await page.selectOption("#filter-stage", "5");
  await expect(page.locator("#showcase-summary")).toContainText("当前筛选 24");
  await expect(page.locator(".monument-card")).toHaveCount(24);
  await page.selectOption("#filter-stage", "all");

  await page.selectOption("#m-type", "relic");
  await page.selectOption("#m-style", "ascii");
  await page.check("#m-public");
  await page.fill("#m-content", "这是一条用于 Pages 演示的本地墓志。 ");
  await page.click("#m-create");
  await expect(page.locator("#showcase-summary")).toContainText("共 126 块碑");
  await expect(page.locator(".monument-card").first()).toContainText("这是一条用于 Pages 演示的本地墓志");

  await page.reload();
  await expect(page.locator("#showcase-summary")).toContainText("共 126 块碑");

  await page.goto("./#/public");
  await expect(page.locator("#public-summary")).toContainText("80 块匿名碑");
  await expect(page.locator(".monument-card")).toHaveCount(36);

  await page.goto("./#/archive");
  await expect(page.locator(".archive-row").first()).toBeVisible();
  expect(await page.locator(".archive-row").count()).toBeGreaterThan(0);

  expect(failedRequests.filter((item) => item.includes("127.0.0.1:8000"))).toEqual([]);
  expect(failedResponses).toEqual([]);
  expect(consoleErrors).toEqual([]);
});
