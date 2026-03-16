from __future__ import annotations

from playwright.sync_api import Page

from framework.pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    def assert_rendered_something(self) -> None:
        self.wait_for_body_visible()
        body_text = self.page.locator("body").inner_text().strip()
        assert body_text, "Page body is empty"

