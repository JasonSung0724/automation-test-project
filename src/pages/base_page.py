import contextlib
from typing import Self

import allure
from playwright.sync_api import expect

from config.settings import settings
from core.base_action import BaseAction
from core.decorators import step


class BasePage(BaseAction):
    URL_PATH: str = "/"

    # Header
    HEADER_TITLE = "[data-testid='header-back-button'] h1"
    HEADER_BACK_BUTTON = "[data-testid='header-back-button']"
    REFRESH_BUTTON = "[data-testid='header-refresh-button']"

    # Loading
    LOADING_INDICATOR = "#loading-indicator"

    # Toast (Sonner)
    TOAST_CONTAINER = "#toast-container"
    TOAST_MESSAGE = "#toast-container [data-sonner-toast]"
    TOAST_SUCCESS = "#toast-container [data-sonner-toast][data-type='success']"
    TOAST_ERROR = "#toast-container [data-sonner-toast][data-type='error']"
    TOAST_WARNING = "#toast-container [data-sonner-toast][data-type='warning']"

    # Confirm Dialog
    CONFIRM_DIALOG_CONFIRM = "[data-testid='confirm-dialog-confirm-button']"
    CONFIRM_DIALOG_CANCEL = "[data-testid='confirm-dialog-cancel-button']"

    # User Navigation
    USER_AVATAR_BUTTON = "[data-testid='user-avatar-button']"
    PROFILE_MENU_ITEM = "[data-testid='profile-menu-item']"
    LOGOUT_MENU_ITEM = "[data-testid='logout-menu-item']"

    def __init__(self, page):
        super().__init__(page)
        self.base_url = settings.BASE_URL

    @property
    def header_back_button(self) -> str:
        return self.locator(self.HEADER_BACK_BUTTON)

    # ============================================================
    # Page Navigation
    # ============================================================

    @allure.step("Navigate to {path}")
    def navigate(self, path: str = None) -> Self:
        path = path or self.URL_PATH
        url = f"{self.base_url}{path}"
        return self.goto(url)

    @allure.step("Wait for page loaded")
    def wait_for_loaded(self, timeout: int = None) -> Self:
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout or self.timeout)
        self.wait_for_loading(timeout)
        return self

    def open(self) -> Self:
        return self.navigate().wait_for_loaded()

    # ============================================================
    # Loading Indicator
    # ============================================================

    @step("Wait for loading to complete")
    def wait_for_loading(self, timeout: int = None) -> Self:
        try:
            self.page.locator(self.LOADING_INDICATOR).wait_for(state="visible", timeout=1000)
        except Exception:
            return self
        self.page.locator(self.LOADING_INDICATOR).wait_for(
            state="hidden", timeout=timeout or self.timeout
        )
        return self

    # ============================================================
    # Toast Notifications
    # ============================================================

    @step("Verify toast message: {expected_text}")
    def expect_toast(self, expected_text: str, toast_type: str = None, timeout: int = None) -> Self:
        if toast_type:
            selector = f"#toast-container [data-sonner-toast][data-type='{toast_type}']"
        else:
            selector = self.TOAST_MESSAGE
        locator = self.page.locator(selector)
        locator.first.wait_for(state="visible", timeout=timeout or self.timeout)
        expect(locator.first).to_contain_text(expected_text)
        return self

    @step("Wait for toast to disappear")
    def wait_for_toast_dismiss(self, timeout: int = None) -> Self:
        with contextlib.suppress(Exception):
            self.page.locator(self.TOAST_MESSAGE).wait_for(
                state="hidden", timeout=timeout or self.timeout
            )
        return self

    # ============================================================
    # Confirm Dialog
    # ============================================================

    @step("Confirm dialog")
    def confirm_dialog(self) -> Self:
        self.click(self.CONFIRM_DIALOG_CONFIRM)
        return self

    @step("Cancel dialog")
    def cancel_dialog(self) -> Self:
        self.click(self.CONFIRM_DIALOG_CANCEL)
        return self

    # ============================================================
    # User Navigation Menu
    # ============================================================

    def has_avatar_menu(self, timeout: int = 3000) -> bool:
        return self.is_visible(self.USER_AVATAR_BUTTON, timeout=timeout)

    @step("Open user menu")
    def open_user_menu(self) -> Self:
        self.page.locator(self.USER_AVATAR_BUTTON).wait_for(state="visible", timeout=10000)
        self.click(self.USER_AVATAR_BUTTON)
        self.wait(300)
        return self

    @step("Navigate to profile via menu")
    def goto_profile(self) -> Self:
        if self.has_avatar_menu():
            self.open_user_menu()
            self.click(self.PROFILE_MENU_ITEM)
        else:
            self.navigate("/profile")
        return self

    @step("Logout via menu")
    def logout(self) -> Self:
        if self.has_avatar_menu():
            self.open_user_menu()
            self.click(self.LOGOUT_MENU_ITEM)
        else:
            self.page.evaluate("window.localStorage.clear()")
            self.page.reload()
        return self

    # ============================================================
    # Utility Methods
    # ============================================================

    def click_and_wait(self, selector: str) -> Self:
        self.click(selector)
        self.wait_for_loaded()
        return self

    def fill_and_submit(self, selector: str, value: str, submit_selector: str = None) -> Self:
        self.fill(selector, value)
        if submit_selector:
            self.click(submit_selector)
        else:
            self.press("Enter")
        return self

    def clear_and_fill(self, selector: str, value: str) -> Self:
        self.clear(selector)
        self.fill(selector, value)
        return self

    def scroll_to(self, selector: str) -> Self:
        self.page.locator(selector).scroll_into_view_if_needed()
        return self

    def get_all_texts(self, selector: str) -> list[str]:
        return self.page.locator(selector).all_text_contents()

    def get_count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    def get_header_title(self) -> str:
        return self.get_text(self.HEADER_TITLE)

    def back_by_header(self) -> Self:
        self.header_back_button.click()
        return self
