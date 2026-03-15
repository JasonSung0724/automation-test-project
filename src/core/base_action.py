from typing import Self

import allure
import pytest
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from core.decorators import retry, step
from core.logger import logger


class BaseAction:
    """Base Playwright actions - Low-level atomic operations."""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = settings.TIMEOUT

    # ============================================================
    # Element Locators
    # ============================================================

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def by_role(self, role: str, name: str = None, **kwargs) -> Locator:
        return self.page.get_by_role(role, name=name, **kwargs)

    def by_text(self, text: str, exact: bool = False) -> Locator:
        return self.page.get_by_text(text, exact=exact)

    def by_label(self, text: str) -> Locator:
        return self.page.get_by_label(text)

    def by_placeholder(self, text: str) -> Locator:
        return self.page.get_by_placeholder(text)

    def by_test_id(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    def by_alt_text(self, text: str) -> Locator:
        return self.page.get_by_alt_text(text)

    def by_title(self, text: str) -> Locator:
        return self.page.get_by_title(text)

    # ============================================================
    # Basic Actions
    # ============================================================

    @step("Click: {selector}")
    def click(self, selector: str) -> Self:
        self.page.click(selector, timeout=self.timeout)
        return self

    @step("Double click: {selector}")
    def double_click(self, selector: str) -> Self:
        self.page.dblclick(selector)
        return self

    @step("Right click: {selector}")
    def right_click(self, selector: str) -> Self:
        self.page.click(selector, button="right")
        return self

    @step("Fill: {selector}")
    def fill(self, selector: str, value: str) -> Self:
        self.page.fill(selector, value)
        return self

    @step("Clear: {selector}")
    def clear(self, selector: str) -> Self:
        self.page.fill(selector, "")
        return self

    @step("Type: {selector}")
    def type_text(self, selector: str, value: str, delay: int = 50) -> Self:
        self.page.locator(selector).press_sequentially(value, delay=delay)
        return self

    @step("Press key: {key}")
    def press(self, key: str) -> Self:
        self.page.keyboard.press(key)
        return self

    @step("Hover: {selector}")
    def hover(self, selector: str) -> Self:
        self.page.hover(selector)
        return self

    @step("Focus: {selector}")
    def focus(self, selector: str) -> Self:
        self.page.focus(selector)
        return self

    @step("Check: {selector}")
    def check(self, selector: str) -> Self:
        self.page.check(selector)
        return self

    @step("Uncheck: {selector}")
    def uncheck(self, selector: str) -> Self:
        self.page.uncheck(selector)
        return self

    @step("Select option: {selector}")
    def select_option(self, selector: str, value: str) -> Self:
        self.page.select_option(selector, value)
        return self

    # ============================================================
    # Get Element Info
    # ============================================================

    def get_text(self, selector: str) -> str:
        return self.page.text_content(selector) or ""

    def get_value(self, selector: str) -> str:
        return self.page.input_value(selector)

    def get_attribute(self, selector: str, attr: str) -> str | None:
        return self.page.get_attribute(selector, attr)

    def is_visible(self, selector: str, timeout: int = 3000) -> bool:
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_checked(self, selector: str) -> bool:
        return self.page.is_checked(selector)

    def is_enabled(self, selector: str) -> bool:
        return self.page.is_enabled(selector)

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    # ============================================================
    # Waits
    # ============================================================

    @retry(max_attempts=3, delay=0.5)
    def wait_for_element(self, selector: str, state: str = "visible") -> Self:
        self.page.locator(selector).wait_for(state=state, timeout=self.timeout)
        return self

    def wait_for_url(self, url_pattern: str) -> Self:
        self.page.wait_for_url(url_pattern, timeout=self.timeout)
        return self

    def wait_for_load_state(self, state: str = "networkidle") -> Self:
        self.page.wait_for_load_state(state, timeout=self.timeout)
        return self

    def wait(self, ms: int) -> Self:
        self.page.wait_for_timeout(ms)
        return self

    # ============================================================
    # Navigation
    # ============================================================

    @step("Go to: {url}")
    def goto(self, url: str) -> Self:
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def reload(self) -> Self:
        self.page.reload()
        return self

    def go_back(self) -> Self:
        self.page.go_back()
        return self

    def go_forward(self) -> Self:
        self.page.go_forward()
        return self

    # ============================================================
    # Screenshots
    # ============================================================

    @step("Screenshot: {name}")
    def screenshot(self, name: str = "screenshot", reason: str = "") -> Self:
        if not self.page.is_closed():
            img = self.page.screenshot()
            allure.attach(img, name=name, attachment_type=allure.attachment_type.PNG)
            logger.info(f"Screenshot: {name}, Reason: {reason}")
            if reason:
                allure.attach(
                    reason,
                    name=f"Screenshot Reason: {reason}",
                    attachment_type=allure.attachment_type.TEXT,
                )
        return self

    # ============================================================
    # Playwright Expect (Assertions)
    # ============================================================

    def expect_visible(self, selector: str, timeout: int = None) -> Self:
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout or self.timeout)
        return self

    def expect_hidden(self, selector: str, timeout: int = None) -> Self:
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout or self.timeout)
        return self

    def expect_not_exist(self, selector: str) -> Self:
        count = self.page.locator(selector).count()
        assert count == 0, f"Expected '{selector}' not to exist, but found {count} element(s)"
        return self

    def expect_not_visible(self, selector: str, timeout: int = 1000) -> Self:
        expect(self.page.locator(selector)).not_to_be_visible(timeout=timeout)
        return self

    def exists(self, selector: str) -> bool:
        return self.page.locator(selector).count() > 0

    def expect_text(self, selector: str, text: str) -> Self:
        expect(self.page.locator(selector)).to_contain_text(text)
        return self

    def expect_value(self, selector: str, value: str) -> Self:
        expect(self.page.locator(selector)).to_have_value(value)
        return self

    def expect_checked(self, selector: str) -> Self:
        expect(self.page.locator(selector)).to_be_checked()
        return self

    def expect_enabled(self, selector: str) -> Self:
        expect(self.page.locator(selector)).to_be_enabled()
        return self

    def expect_disabled(self, selector: str) -> Self:
        expect(self.page.locator(selector)).to_be_disabled()
        return self

    def expect_url(self, url: str) -> Self:
        expect(self.page).to_have_url(url, timeout=self.timeout)
        return self

    def expect_url_contains(self, text: str) -> Self:
        import re

        expect(self.page).to_have_url(re.compile(re.escape(text)), timeout=self.timeout)
        return self

    def expect_title(self, title: str) -> Self:
        expect(self.page).to_have_title(title)
        return self

    @step("Verify assertion")
    def assertion(self, condition: bool, message: str = "") -> bool:
        if not condition:
            self.screenshot(message)
        return pytest.assume(condition, message)

    # ============================================================
    # Properties
    # ============================================================

    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title()
