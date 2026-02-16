from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page


@dataclass(frozen=True)
class BasePage:
    page: Page
    base_url: str

    def goto(self, path: str = "/", *, wait_until: str = "domcontentloaded") -> None:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        self.page.goto(url, wait_until=wait_until)

    def wait_for_body_visible(self, timeout_ms: int = 15_000) -> None:
        self.page.locator("body").wait_for(state="visible", timeout=timeout_ms)

