import { expect, test } from "@playwright/test";

test("login screen is available", async ({ page }) => {
  await page.goto("/login");
  await expect(
    page.getByRole("heading", { name: "Company Web" }),
  ).toBeVisible();
});
