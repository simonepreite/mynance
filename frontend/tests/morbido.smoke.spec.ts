import { expect, type Page, test } from "@playwright/test"

// Story 1.2: shared Morbido component library + accessibility floor.
// Exercised against the dev-only gallery (morbido-gallery.html), served by the
// Vite dev server, in the no-auth `theme` Playwright project.

const GALLERY = "/morbido-gallery.html"

const readVar = (name: string) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim()

async function gotoLight(page: Page) {
  await page.addInitScript(() => localStorage.setItem("mynance-theme", "light"))
  await page.goto(GALLERY)
}

test("AC1: documented tokens (incl. typography) are available as CSS vars", async ({
  page,
}) => {
  await gotoLight(page)
  // colour tokens
  expect(await page.evaluate(readVar, "--m-bg")).toBe("#f4f1ea")
  expect(await page.evaluate(readVar, "--m-surface")).toBe("#fbfaf6")
  expect(await page.evaluate(readVar, "--m-ink")).toBe("#3a3a38")
  expect(await page.evaluate(readVar, "--m-ink-soft")).toBe("#6d6a63")
  expect(await page.evaluate(readVar, "--m-honesty")).toBe("#8b6237")
  expect(await page.evaluate(readVar, "--m-negative")).toBe("#a05c43")
  expect(await page.evaluate(readVar, "--m-focus")).toBe("#527a6d")
  expect(await page.evaluate(readVar, "--radius-card-base")).toBe("2.125rem")
  // typography tokens
  expect(await page.evaluate(readVar, "--font-sans")).toContain("-apple-system")
  expect(await page.evaluate(readVar, "--type-display")).toContain("2.875rem")
  expect(await page.evaluate(readVar, "--type-body")).toContain("0.9375rem")
})

test("AC1: switching theme re-resolves tokens without a reload", async ({
  page,
}) => {
  await gotoLight(page)
  expect(await page.evaluate(readVar, "--m-bg")).toBe("#f4f1ea")
  await page.getByTestId("set-dark").click()
  await expect(page.getByTestId("current-theme")).toHaveText("dark")
  await expect.poll(() => page.evaluate(readVar, "--m-bg")).toBe("#21201d")
})

test("AC2: the shared component library renders", async ({ page }) => {
  await gotoLight(page)
  for (const id of [
    "card",
    "balance-block",
    "bottom-nav",
    "honesty-banner",
    "list-row",
    "chip",
    "focus-probe",
    "input",
  ]) {
    await expect(page.getByTestId(id)).toBeVisible()
  }
})

test("AC3: keyboard focus shows a 2px focus-token ring", async ({ page }) => {
  await gotoLight(page)
  // Tab to the first focusable element (the focus-probe button).
  let testid: string | null = null
  for (let i = 0; i < 6 && testid !== "focus-probe"; i++) {
    await page.keyboard.press("Tab")
    testid = await page.evaluate(
      () => document.activeElement?.getAttribute("data-testid") ?? null,
    )
  }
  expect(testid).toBe("focus-probe")
  const shadow = await page.evaluate(
    () => getComputedStyle(document.activeElement as Element).boxShadow,
  )
  // ring-focus = color.focus (#527A6D → rgb(82,122,109)); never the soft accent.
  expect(shadow).toContain("82, 122, 109")
  expect(shadow).not.toBe("none")
})

test("AC4: every tap target is at least 44px", async ({ page }) => {
  await gotoLight(page)
  const targets = page.locator("[data-tap-target]")
  const count = await targets.count()
  expect(count).toBeGreaterThan(0)
  for (let i = 0; i < count; i++) {
    const box = await targets.nth(i).boundingBox()
    expect(box).not.toBeNull()
    if (box) {
      expect(box.height).toBeGreaterThanOrEqual(43.5)
      expect(box.width).toBeGreaterThanOrEqual(43.5)
    }
  }
})

test("AC5: honesty banner uses warm amber, never alarm-red", async ({
  page,
}) => {
  await gotoLight(page)
  const banner = page.getByTestId("honesty-banner")
  const color = await banner.evaluate((el) => getComputedStyle(el).color)
  const bg = await banner.evaluate((el) => getComputedStyle(el).backgroundColor)
  expect(color).toBe("rgb(139, 98, 55)") // #8B6237 amber ink
  expect(bg).toBe("rgb(246, 233, 216)") // #F6E9D8 amber bg
})

test("AC5: sign is never conveyed by colour alone (+/− glyph present)", async ({
  page,
}) => {
  await gotoLight(page)
  await expect(page.getByTestId("balance-block")).toContainText("+")
  await expect(page.getByTestId("balance-block-negative")).toContainText("−")
})

test("AC6: Reduce Motion shows the end state immediately", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" })
  await page.addInitScript(() => localStorage.setItem("mynance-theme", "light"))
  await page.goto(GALLERY)
  const banner = page.getByTestId("honesty-banner")
  await expect(banner).toBeVisible()
  // The entrance animation is neutralized → the element is at full opacity.
  await expect
    .poll(() => banner.evaluate((el) => getComputedStyle(el).opacity))
    .toBe("1")
})
