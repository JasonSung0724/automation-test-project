from typing import Self

from pages.base_page import BasePage


class RulesPage(BasePage):
    """Page Object for Rules (定期記帳) management."""

    URL_PATH = "/group"

    # Header
    HEADER_TITLE = "h1"
    BACK_BUTTON = "[data-testid='header-back-button']"

    # Tab buttons (on rules page)
    ADD_RECURRING_BTN = "button:has-text('定期記帳'), button:has-text('Recurring')"
    ADD_REPAYMENT_BTN = "button:has-text('定期還款'), button:has-text('Repayment')"

    # Empty state
    EMPTY_STATE_TEXT = "p"  # Will check content programmatically

    # Rule Dialog
    DIALOG = "[role='dialog']"
    DIALOG_TITLE = "[role='dialog'] h2"
    DIALOG_CLOSE_BTN = "[role='dialog'] button:has-text('Close')"

    # Dialog - Type tabs (data-testid)
    TAB_EXPENSE = "[data-testid='recurring-rule-expense-tab']"
    TAB_INCOME = "[data-testid='recurring-rule-income-tab']"

    # Dialog - Form fields (data-testid)
    TITLE_INPUT = "[data-testid='recurring-rule-title-input']"
    AMOUNT_INPUT = "[data-testid='recurring-rule-amount-input']"
    CURRENCY_SELECT = "[data-testid='recurring-rule-currency-trigger']"
    START_DATE_BTN = "[data-testid='recurring-rule-start-date-trigger']"
    NOTE_INPUT = "[data-testid='recurring-rule-note-input']"

    # Dialog - Duration options (data-testid)
    DURATION_CONTINUOUS = "[data-testid='recurring-rule-duration-continuous-button']"
    DURATION_FIXED = "[data-testid='recurring-rule-duration-fixed-button']"

    # Dialog - Actions (data-testid)
    CANCEL_BTN = "[data-testid='recurring-rule-cancel-button']"
    SUBMIT_BTN = "[data-testid='recurring-rule-submit-button']"

    # Category buttons (data-testid)
    CATEGORY_FOOD = "[data-testid='category-button-food']"
    CATEGORY_TRANSPORT = "[data-testid='category-button-transport']"
    CATEGORY_DRINK = "[data-testid='category-button-drink']"
    CATEGORY_FLIGHT = "[data-testid='category-button-flight']"
    CATEGORY_HOTEL = "[data-testid='category-button-hotel']"
    CATEGORY_TICKET = "[data-testid='category-button-ticket']"
    CATEGORY_SHOPPING = "[data-testid='category-button-shopping']"
    CATEGORY_FUEL = "[data-testid='category-button-fuel']"
    CATEGORY_ENTERTAINMENT = "[data-testid='category-button-entertainment']"
    CATEGORY_CAR = "[data-testid='category-button-car']"
    CATEGORY_SNACK = "[data-testid='category-button-snack']"
    CATEGORY_COFFEE = "[data-testid='category-button-coffee']"
    CATEGORY_BEER = "[data-testid='category-button-beer']"
    CATEGORY_MEDICAL = "[data-testid='category-button-medical']"
    CATEGORY_GIFT = "[data-testid='category-button-gift']"
    CATEGORY_OTHER = "[data-testid='category-button-other']"

    # Rule cards (when rules exist)
    RULE_CARD = "[data-testid^='rule-card-']"

    def get_category_selector(self, category: str) -> str:
        """Get selector for a category button by key."""
        return f"[data-testid='category-button-{category}']"

    def get_rule_card(self, rule_id: str) -> str:
        """Get selector for a specific rule card."""
        return f"[data-testid='rule-card-{rule_id}']"

    def open_rules(self, group_id: str) -> Self:
        """Navigate to the rules page for a group."""
        self.navigate(f"/group/{group_id}/rules")
        self.wait_for_loaded()
        return self

    def click_add_recurring(self) -> Self:
        """Click the add recurring rule button."""
        self.click(self.ADD_RECURRING_BTN)
        self.wait_for_element(self.DIALOG, state="visible")
        return self

    def click_add_repayment(self) -> Self:
        """Click the add repayment rule button."""
        self.click(self.ADD_REPAYMENT_BTN)
        self.wait_for_element(self.DIALOG, state="visible")
        return self

    def select_type(self, rule_type: str = "expense") -> Self:
        """Select rule type (expense or income)."""
        if rule_type == "income":
            self.click(self.TAB_INCOME)
        else:
            self.click(self.TAB_EXPENSE)
        return self

    def fill_title(self, title: str) -> Self:
        """Fill the rule title."""
        self.fill(self.TITLE_INPUT, title)
        return self

    def fill_amount(self, amount: str) -> Self:
        """Fill the rule amount."""
        self.fill(self.AMOUNT_INPUT, amount)
        return self

    def select_category(self, category: str) -> Self:
        """Select a category for the rule.

        Args:
            category: Category key like 'food', 'transport', 'shopping', 'other'
        """
        selector = self.get_category_selector(category)
        self.click(selector)
        return self

    def fill_note(self, note: str) -> Self:
        """Fill the note field."""
        self.fill(self.NOTE_INPUT, note)
        return self

    def select_duration(self, continuous: bool = True) -> Self:
        """Select duration type."""
        if continuous:
            self.click(self.DURATION_CONTINUOUS)
        else:
            self.click(self.DURATION_FIXED)
        return self

    def submit_rule(self, wait_for_close: bool = True) -> Self:
        """Submit the rule form.

        Args:
            wait_for_close: Whether to wait for dialog to close (default True)
        """
        self.click(self.SUBMIT_BTN)
        if wait_for_close:
            # Wait for dialog to close, but don't fail if it doesn't
            try:
                self.wait_for_element(self.DIALOG, state="hidden")
            except Exception:
                # Dialog might stay open due to validation errors
                pass
        return self

    def cancel_rule(self) -> Self:
        """Cancel the rule form."""
        self.click(self.CANCEL_BTN)
        self.wait_for_element(self.DIALOG, state="hidden")
        return self

    def close_dialog(self) -> Self:
        """Close the dialog via close button."""
        self.click(self.DIALOG_CLOSE_BTN)
        self.wait_for_element(self.DIALOG, state="hidden")
        return self

    def create_recurring_rule(
        self,
        title: str,
        amount: str,
        category: str = "other",
        rule_type: str = "expense",
        note: str = "",
    ) -> Self:
        """Create a new recurring rule with all steps.

        Args:
            title: Rule title
            amount: Amount value
            category: Category key like 'food', 'transport', 'shopping', 'other'
            rule_type: 'expense' or 'income'
            note: Optional note
        """
        self.click_add_recurring()
        self.select_type(rule_type)
        self.fill_title(title)
        self.fill_amount(amount)
        self.select_category(category)
        if note:
            self.fill_note(note)
        self.submit_rule()
        return self

    def is_empty_state(self) -> bool:
        """Check if the page shows empty state (no rules)."""
        return not self.is_visible(self.RULE_CARD, timeout=2000)

    def get_rule_count(self) -> int:
        """Get the number of rule cards."""
        return self.count(self.RULE_CARD)

    def is_dialog_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.is_visible(self.DIALOG, timeout=2000)
