from typing import Self

from playwright.sync_api import Page

from core.decorators import step
from pages.base_page import BasePage


class BalancePage(BasePage):
    URL_PATH = "/group"

    SETTLEMENT_SETTLE_BTN = "[data-testid='settlement-settle-button']"
    SETTLEMENT_CONFIRM_BTN = "[data-testid='settlement-confirm-button']"
    SETTLEMENT_CANCEL_BTN = "[data-testid='settlement-cancel-button']"

    def __init__(self, page: Page):
        super().__init__(page)

    def open_balance(self, group_id: str) -> Self:
        return self.navigate(f"/group/{group_id}/balance").wait_for_loaded()

    @step("Click settle")
    def click_settle(self) -> Self:
        self.click(self.SETTLEMENT_SETTLE_BTN)
        return self

    @step("Confirm settlement")
    def confirm_settlement(self) -> Self:
        self.click(self.SETTLEMENT_CONFIRM_BTN)
        return self

    @step("Cancel settlement")
    def cancel_settlement(self) -> Self:
        self.click(self.SETTLEMENT_CANCEL_BTN)
        return self
