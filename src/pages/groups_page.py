from typing import Self

import allure
from playwright.sync_api import Locator, Page

from core.decorators import step
from pages.base_page import BasePage


class GroupsPage(BasePage):
    URL_PATH = "/groups"

    PERSONAL_GROUP_CARD = "[data-testid='personal-ledger-card']"
    CREATE_GROUP_BTN = "[data-testid='create-group-button']"
    CREATE_GROUP_EMPTY_BTN = "[data-testid='create-group-empty-button']"
    CREATE_GROUP_SUBMIT_BTN = "[data-testid='create-group-submit-button']"
    GROUP_NAME_INPUT = "[data-testid='group-name-input']"
    GROUP_SEARCH_INPUT = "[data-testid='group-search-input']"
    GROUP_SEARCH_CLEAR = "[data-testid='group-search-clear-button']"
    VIEW_SIZE_TOGGLE = "[data-testid='view-size-toggle-button']"
    GROUP_CARD = "[data-testid^='group-card-']"

    def __init__(self, page: Page):
        super().__init__(page)

    def click_personal_group_card(self) -> Self:
        self.click(self.PERSONAL_GROUP_CARD)
        return self

    def click_group_card_by_id(self, group_id: str) -> Self:
        self.click(f"[data-testid='group-card-{group_id}']")
        return self

    def click_group_card_by_name(self, name: str) -> Self:
        self.by_text(name).click()
        return self

    @step("Click create group")
    def click_create_group(self) -> Self:
        self.click(self.CREATE_GROUP_BTN)
        return self

    @step("Fill group name: {name}")
    def fill_group_name(self, name: str) -> Self:
        self.fill(self.GROUP_NAME_INPUT, name)
        return self

    @step("Submit create group")
    def submit_create_group(self) -> Self:
        self.click(self.CREATE_GROUP_SUBMIT_BTN)
        return self

    @step("Create group: {name}")
    def create_group(self, name: str) -> Self:
        self.click_create_group()
        self.fill_group_name(name)
        self.submit_create_group()
        self.wait_for_loading()
        return self

    @step("Search groups: {keyword}")
    def search_group(self, keyword: str) -> Self:
        self.fill(self.GROUP_SEARCH_INPUT, keyword)
        return self

    @step("Clear group search")
    def clear_search(self) -> Self:
        self.click(self.GROUP_SEARCH_CLEAR)
        return self

    @step("Toggle view size")
    def toggle_view_size(self) -> Self:
        self.click(self.VIEW_SIZE_TOGGLE)
        return self

    def get_group_cards(self) -> list[Locator]:
        return self.page.locator(self.GROUP_CARD).all()

    def get_group_count(self) -> int:
        return len(self.get_group_cards())

    @allure.step("Click group at index {index}")
    def click_group_by_index(self, index: int = 0) -> Self:
        cards = self.get_group_cards()
        if cards:
            cards[index].click()
        return self
