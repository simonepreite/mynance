import { expect, test } from "@playwright/test"

// Story 1.1, AC5: visual styling derives from the "Morbido" tokens in both
// light and dark, switchable. We assert the computed body colors AND a
// representative set of raw Morbido tokens (color.surface, color.accent, a
// radius, plus ink in both modes) resolve to the documented values (DESIGN.md)
// — proving the theme is Morbido (not the template default) and that light/dark
// switching works, with no default leaking.

const LIGHT_BG = "rgb(244, 241, 234)" // #F4F1EA color.bg light
const LIGHT_INK = "rgb(58, 58, 56)" // #3A3A38 color.ink light
const DARK_BG = "rgb(33, 32, 29)" // #21201D color.bg dark

const readBg = () => getComputedStyle(document.body).backgroundColor
const readInk = () => getComputedStyle(document.body).color
const readVar = (name: string) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim()

test("light theme renders Morbido tokens", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("mynance-theme", "light"))
  await page.goto("/login")
  await expect.poll(() => page.evaluate(readBg)).toBe(LIGHT_BG)
  expect(await page.evaluate(readInk)).toBe(LIGHT_INK)
  // Representative token set (raw --m-* + a radius) — no template default leaking.
  expect(await page.evaluate(readVar, "--m-surface")).toBe("#fbfaf6")
  expect(await page.evaluate(readVar, "--m-accent")).toBe("#7fa99b")
  expect(await page.evaluate(readVar, "--m-ink")).toBe("#3a3a38")
  expect(await page.evaluate(readVar, "--radius")).toBe("1.125rem")
})

test("dark theme renders warm Morbido tokens", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("mynance-theme", "dark"))
  await page.goto("/login")
  await expect.poll(() => page.evaluate(readBg)).toBe(DARK_BG)
  // Dark mode flips the raw tokens (warm browns) — surface, accent, and ink.
  expect(await page.evaluate(readVar, "--m-surface")).toBe("#2c2a27")
  expect(await page.evaluate(readVar, "--m-accent")).toBe("#9cc4b5")
  expect(await page.evaluate(readVar, "--m-ink")).toBe("#ece7dd")
})
