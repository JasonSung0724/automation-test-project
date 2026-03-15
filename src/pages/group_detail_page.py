from typing import Literal, Self

from playwright.sync_api import Page

from core.decorators import step
from pages.base_page import BasePage

TransactionType = Literal["expense", "income", "transfer"]


class GroupDetailPage(BasePage):
    URL_PATH = "/group"

    # Tab Locators
    SHARE_TAB = "[data-testid='action-share-button']"
    PERSONAL_LEDGER_TAB = "[data-testid='action-personal-ledger-button']"
    BALANCE_TAB = "[data-testid='action-balance-button']"
    SETTING_TAB = "[data-testid='action-settings-button']"
    RULE_TAB = "[data-testid='action-rules-button']"
    STATS_TAB = "[data-testid='action-stats-button']"
    BUDGET_TAB = "[data-testid='action-budget-button']"
    IMPORT_TAB = "[data-testid='action-import-button']"
    EXPORT_TAB = "[data-testid='action-export-button']"

    # Filter Locators
    FILTER_TYPE_BUTTON = "[data-testid='transaction-type-filter-{filter_type}-button']"
    FILTER_ALL = "[data-testid='transaction-type-filter-all-button']"
    FILTER_INCOME = "[data-testid='transaction-type-filter-income-button']"
    FILTER_EXPENSE = "[data-testid='transaction-type-filter-expense-button']"
    FILTER_TRANSFER = "[data-testid='transaction-type-filter-transfer-button']"

    # Action Locators
    ADD_TRANSACTION_BTN = "[data-testid='add-transaction-button']"

    # View Type Locators
    VIEW_MODE_BUTTON = "[data-testid='view-mode-{view}-button']"
    VIEW_LIST = "[data-testid='view-mode-list-button']"
    VIEW_CALENDAR = "[data-testid='view-mode-calendar-button']"
    VIEW_LOGS = "[data-testid='view-mode-logs-button']"

    # Transaction Form Locators
    TAB_LIST = "[role='tablist']"
    TITLE_INPUT = "[data-testid='transaction-item-input']"
    AMOUNT_INPUT = "[data-testid='transaction-amount-input']"
    NOTE_INPUT = "[data-testid='transaction-note-input']"
    CONFIRM_BTN = "[data-testid='transaction-confirm-button']"
    CANCEL_BTN = "[data-testid='transaction-cancel-button']"

    # Transaction Search
    TRANSACTION_CARD = "[data-testid='transaction-card-{transaction_id}']"
    TRANSACTION_SEARCH_INPUT = "[data-testid='transaction-search-input']"
    TRANSACTION_SEARCH_CLEAR = "[data-testid='transaction-search-clear-button']"

    # Category
    CATEGORY_SEARCH_INPUT = "[data-testid='category-search-input']"
    CATEGORY_BUTTON = "[data-testid='category-button-{icon_id}']"

    # Member Picker
    MEMBER_PICKER_TRIGGER = "[data-testid='member-picker-trigger']"
    MEMBER_PICKER_CONFIRM = "[data-testid='member-picker-confirm-button']"
    MEMBER_PICKER_OPTION = "[data-testid='member-picker-option-{member_id}']"

    # Splits
    SPLIT_RESET_BTN = "[data-testid='split-reset-button']"
    SPLIT_AMOUNT_INPUT = "[data-testid='split-amount-input-{member_id}']"
    SPLIT_EXCLUDE_BUTTON = "[data-testid='split-exclude-button-{member_id}']"

    # Transaction Type Tabs
    TYPE_TAB = {
        "expense": "[data-testid='transaction-type-expense-tab']",
        "income": "[data-testid='transaction-type-income-tab']",
        "transfer": "[data-testid='transaction-type-transfer-tab']",
    }

    def __init__(self, page: Page):
        super().__init__(page)

    # ============================================================
    # Transaction CRUD
    # ============================================================

    @step("Create transaction via UI")
    def _create_transaction_interface(
        self, title: str, amount: str, t_type: TransactionType = "expense", note: str = ""
    ) -> Self:
        self.click(self.ADD_TRANSACTION_BTN)
        self.wait(300)
        tab = self.TYPE_TAB[t_type]
        if self.is_visible(tab) and self.get_attribute(tab, "data-state") != "active":
            self.click(tab)
        self.fill(self.TITLE_INPUT, title)
        self.fill(self.AMOUNT_INPUT, amount)
        if note:
            self.fill(self.NOTE_INPUT, note)
        self.click(self.CONFIRM_BTN)
        self.expect_hidden(self.CONFIRM_BTN)
        return self

    @step("Create transaction and get response")
    def create_transaction(
        self, title: str, amount: str, t_type: TransactionType = "expense", note: str = ""
    ) -> dict:
        with self.page.expect_response(
            lambda resp: "/api/transactions/group/" in resp.url and resp.request.method == "POST"
        ) as response_info:
            self._create_transaction_interface(title, amount, t_type, note)
            res = response_info.value
            if res.status == 201:
                return res.json()
            raise Exception(f"Failed to create transaction: {res.status} {res.status_text}")

    def open_transaction(self, transaction_id: str) -> Self:
        self.click(f"[data-testid='transaction-card-{transaction_id}']")
        return self

    def open_group(self, group_id: str) -> Self:
        return self.navigate(f"/group/{group_id}").wait_for_loaded()

    # ============================================================
    # Transaction Filters & Search
    # ============================================================

    @step("Filter by type: {filter_type}")
    def filter_by_type(self, filter_type: str) -> Self:
        self.click(self.FILTER_TYPE_BUTTON.format(filter_type=filter_type))
        return self

    @step("Search transactions: {keyword}")
    def search_transaction(self, keyword: str) -> Self:
        self.fill(self.TRANSACTION_SEARCH_INPUT, keyword)
        return self

    @step("Clear transaction search")
    def clear_search(self) -> Self:
        self.click(self.TRANSACTION_SEARCH_CLEAR)
        return self

    # ============================================================
    # View Modes
    # ============================================================

    @step("Switch view: {view}")
    def switch_view(self, view: str) -> Self:
        self.click(self.VIEW_MODE_BUTTON.format(view=view))
        return self

    # ============================================================
    # Category & Member
    # ============================================================

    @step("Select category: {icon_id}")
    def select_category(self, icon_id: str) -> Self:
        self.click(self.CATEGORY_BUTTON.format(icon_id=icon_id))
        return self

    @step("Select member: {member_id}")
    def select_member(self, member_id: str) -> Self:
        self.click(self.MEMBER_PICKER_TRIGGER)
        self.click(self.MEMBER_PICKER_OPTION.format(member_id=member_id))
        self.click(self.MEMBER_PICKER_CONFIRM)
        return self

    @step("Set split amount: {member_id} = {amount}")
    def set_split_amount(self, member_id: str, amount: str) -> Self:
        self.fill(self.SPLIT_AMOUNT_INPUT.format(member_id=member_id), amount)
        return self

    @step("Exclude from split: {member_id}")
    def exclude_from_split(self, member_id: str) -> Self:
        self.click(self.SPLIT_EXCLUDE_BUTTON.format(member_id=member_id))
        return self

    def get_transaction_card(self, transaction_id: str) -> str:
        return self.TRANSACTION_CARD.format(transaction_id=transaction_id)

    # ============================================================
    # Quick Actions
    # ============================================================

    @step("Click add transaction")
    def click_add_transaction(self) -> Self:
        self.click(self.ADD_TRANSACTION_BTN)
        return self

    @step("Fill amount: {amount}")
    def fill_amount(self, amount: str) -> Self:
        self.fill(self.AMOUNT_INPUT, amount)
        return self

    @step("Fill title: {title}")
    def fill_title(self, title: str) -> Self:
        self.fill(self.TITLE_INPUT, title)
        return self

    @step("Submit transaction")
    def submit_transaction(self) -> Self:
        self.click(self.CONFIRM_BTN)
        return self
