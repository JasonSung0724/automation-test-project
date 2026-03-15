from typing import Self

from playwright.sync_api import Page

from core.decorators import step
from pages.base_page import BasePage


class GroupSettingsPage(BasePage):
    URL_PATH = "/group"

    ADD_MEMBER_BTN = "[data-testid='add-member-button']"
    CURRENCY_SELECT_TRIGGER = "[data-testid='currency-select-trigger']"
    ADD_CURRENCY_BTN = "[data-testid='add-currency-button']"
    LANGUAGE_SWITCHER = "[data-testid='language-switcher-trigger']"

    def __init__(self, page: Page):
        super().__init__(page)

    def open_settings(self, group_id: str) -> Self:
        return self.navigate(f"/group/{group_id}/settings").wait_for_loaded()

    def open_members(self, group_id: str) -> Self:
        return self.navigate(f"/group/{group_id}/members").wait_for_loaded()

    @step("Add member: {name}")
    def add_member(self, name: str, index: int = 0) -> Self:
        self.click(self.ADD_MEMBER_BTN)
        self.fill(f"[data-testid='member-name-input-{index}']", name)
        return self

    @step("Remove member at index {index}")
    def remove_member(self, index: int) -> Self:
        self.click(f"[data-testid='remove-member-button-{index}']")
        return self

    @step("Select currency: {code}")
    def select_currency(self, code: str) -> Self:
        self.click(self.CURRENCY_SELECT_TRIGGER)
        self.click(f"[data-testid='primary-currency-option-{code}']")
        return self

    @step("Switch language: {code}")
    def switch_language(self, code: str) -> Self:
        self.click(self.LANGUAGE_SWITCHER)
        self.click(f"[data-testid='language-option-{code}']")
        return self
