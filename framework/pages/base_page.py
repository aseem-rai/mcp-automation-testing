from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page

from framework.utils.logger import logger
from framework.utils.settings import settings


@dataclass(frozen=True)
class BasePage:
    page: Page
    base_url: str

    def goto(self, path: str = "/", *, wait_until: str = "domcontentloaded") -> None:
        url = f"{settings.BASE_URL}/{path.lstrip('/')}"
        logger.info("Navigating to %s", path or "/")
        self.page.goto(url, wait_until=wait_until)
        # Global stabilization delay requested for every page navigation.
        self.page.wait_for_timeout(10_000)

    def wait_for_body_visible(self, timeout_ms: int = 15_000) -> None:
        self.page.locator("body").wait_for(state="visible", timeout=timeout_ms)

