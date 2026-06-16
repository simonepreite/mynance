import { expect, test } from "@playwright/test"

// Story 1.1, AC5: visual styling derives from the "Morbido" tokens in both
// light and dark, switchable. We assert the computed body colors resolve to the
// documented Morbido values (DESIGN.md) — proving the theme is Morbido (not the
// template default) and that light/dark switching works.

const LIGHT_BG = "rgb(244, 241, 234)" // #F4F1EA color.bg light
const LIGHT_INK = "rgb(58, 58, 56)" // #3A3A38 color.ink light
const DARK_BG = "rgb(33, 32, 29)" // #21201D color.bg dark

const readBg = () => getComputedStyle(document.body).backgroundColor
const readInk = () => getComputedStyle(document.body).color

test("light theme renders Morbido tokens", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("mynance-theme", "light"))
  await page.goto("/login")
  await expect.poll(() => page.evaluate(readBg)).toBe(LIGHT_BG)
  expect(await page.evaluate(readInk)).toBe(LIGHT_INK)
})

test("dark theme renders warm Morbido tokens", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("mynance-theme", "dark"))
  await page.goto("/login")
  await expect.poll(() => page.evaluate(readBg)).toBe(DARK_BG)
})
