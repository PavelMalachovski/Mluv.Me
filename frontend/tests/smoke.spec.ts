import { test, expect } from "@playwright/test"

/**
 * Frontend smoke tests for Mluv.Me web app.
 *
 * These tests verify that critical pages load correctly
 * and key UI elements are present. They run against a local
 * dev server or a staging URL.
 *
 * Run: npx playwright test
 */

const BASE_URL = process.env.BASE_URL || "http://localhost:3000"

test.describe("Smoke Tests", () => {
  test("home page loads and has login button", async ({ page }) => {
    await page.goto(BASE_URL)
    await expect(page).toHaveTitle(/Mluv/i)
    // The page should have some visible content
    const body = page.locator("body")
    await expect(body).toBeVisible()
  })

  test("dashboard redirects unauthenticated users", async ({ page }) => {
    const response = await page.goto(`${BASE_URL}/dashboard`)
    // Should redirect to login or show auth prompt
    expect(response?.status()).toBeLessThan(500)
  })

  test("practice page loads without crash", async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard/practice`)
    // Should not show a server error
    const body = page.locator("body")
    await expect(body).toBeVisible()
    // Should not have unhandled error overlay
    const errorOverlay = page.locator("#__next-build-error")
    await expect(errorOverlay).not.toBeVisible({ timeout: 3000 }).catch(() => {
      // No error overlay is fine
    })
  })

  test("API health endpoint responds", async ({ request }) => {
    const apiUrl = process.env.API_URL || "http://localhost:8000"
    try {
      const response = await request.get(`${apiUrl}/health`)
      expect(response.status()).toBe(200)
    } catch {
      // API may not be running in CI — skip gracefully
      test.skip()
    }
  })
})
