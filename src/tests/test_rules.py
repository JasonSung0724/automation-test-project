import allure
import pytest

from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Rules")
@allure.epic("Group Management")
@allure.feature("Recurring Rules")
@pytest.mark.rules
class TestRulesPage:
    """Tests for the Rules (定期記帳) feature."""

    @allure.story("Rules Page Loads")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_rules_page_loads(self, pages: Pages, personal_ledger: dict):
        """Test that the rules page loads correctly."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])

        with allure.step("Verify page header is visible"):
            pom.expect_url_contains("/rules")

        with allure.step("Verify add buttons are visible"):
            pom.expect_visible(pom.ADD_RECURRING_BTN)
            pom.expect_visible(pom.ADD_REPAYMENT_BTN)

        pom.screenshot("rules_page_loaded")

    @allure.story("Empty State Display")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_state_displayed(self, pages: Pages, personal_ledger: dict):
        """Test that empty state is shown when no rules exist."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])

        with allure.step("Verify empty state message"):
            assert pom.is_empty_state(), "Empty state should be displayed"

        pom.screenshot("rules_empty_state")

    @allure.story("Add Recurring Dialog Opens")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_add_recurring_dialog_opens(self, pages: Pages, personal_ledger: dict):
        """Test that clicking add recurring opens the dialog."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])

        with allure.step("Click add recurring button"):
            pom.click_add_recurring()

        with allure.step("Verify dialog is visible"):
            pom.expect_visible(pom.DIALOG)
            pom.expect_visible(pom.TITLE_INPUT)
            pom.expect_visible(pom.AMOUNT_INPUT)
            pom.expect_visible(pom.SUBMIT_BTN)

        pom.screenshot("add_recurring_dialog")

        with allure.step("Close dialog"):
            pom.cancel_rule()

    @allure.story("Dialog Type Tabs Work")
    @allure.severity(allure.severity_level.NORMAL)
    def test_dialog_type_tabs(self, pages: Pages, personal_ledger: dict):
        """Test that expense/income tabs work in the dialog."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])
        pom.click_add_recurring()

        with allure.step("Verify expense tab is selected by default"):
            pom.expect_visible(pom.TAB_EXPENSE)

        with allure.step("Switch to income tab"):
            pom.select_type("income")

        pom.screenshot("income_tab_selected")

        with allure.step("Switch back to expense tab"):
            pom.select_type("expense")

        pom.cancel_rule()

    @allure.story("Category Selection Works")
    @allure.severity(allure.severity_level.NORMAL)
    def test_category_selection(self, pages: Pages, personal_ledger: dict):
        """Test that category buttons are clickable."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])
        pom.click_add_recurring()

        with allure.step("Verify category buttons are visible"):
            pom.expect_visible(pom.CATEGORY_FOOD)
            pom.expect_visible(pom.CATEGORY_TRANSPORT)
            pom.expect_visible(pom.CATEGORY_SHOPPING)

        with allure.step("Click a category"):
            pom.select_category("food")

        pom.screenshot("category_selected")
        pom.cancel_rule()

    @allure.story("Duration Options Work")
    @allure.severity(allure.severity_level.NORMAL)
    def test_duration_options(self, pages: Pages, personal_ledger: dict):
        """Test that duration options (continuous/fixed) work."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])
        pom.click_add_recurring()

        with allure.step("Verify duration buttons are visible"):
            pom.expect_visible(pom.DURATION_CONTINUOUS)
            pom.expect_visible(pom.DURATION_FIXED)

        with allure.step("Select fixed duration"):
            pom.select_duration(continuous=False)

        pom.screenshot("fixed_duration_selected")
        pom.cancel_rule()

    @allure.story("Cancel Button Closes Dialog")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cancel_closes_dialog(self, pages: Pages, personal_ledger: dict):
        """Test that cancel button closes the dialog."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])
        pom.click_add_recurring()

        with allure.step("Verify dialog is open"):
            pom.expect_visible(pom.DIALOG)

        with allure.step("Click cancel"):
            pom.cancel_rule()

        with allure.step("Verify dialog is closed"):
            pom.expect_hidden(pom.DIALOG)

        pom.screenshot("dialog_closed")

    @allure.story("Form Validation - Empty Title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_validation_empty_title(self, pages: Pages, personal_ledger: dict):
        """Test that form requires a title."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])
        pom.click_add_recurring()

        with allure.step("Fill only amount"):
            pom.fill_amount("100")

        with allure.step("Try to submit"):
            pom.click(pom.SUBMIT_BTN)

        with allure.step("Dialog should still be open (validation failed)"):
            pom.expect_visible(pom.DIALOG)

        pom.screenshot("validation_empty_title")
        pom.cancel_rule()

    @allure.story("Form Validation - Empty Amount")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_validation_empty_amount(self, pages: Pages, personal_ledger: dict):
        """Test that form requires an amount."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])
        pom.click_add_recurring()

        with allure.step("Fill only title"):
            pom.fill_title("Test Rule")

        with allure.step("Try to submit"):
            pom.click(pom.SUBMIT_BTN)

        with allure.step("Dialog should still be open (validation failed)"):
            pom.expect_visible(pom.DIALOG)

        pom.screenshot("validation_empty_amount")
        pom.cancel_rule()


@allure.parent_suite("E2E Tests")
@allure.suite("Rules")
@allure.epic("Group Management")
@allure.feature("Recurring Rules CRUD")
@pytest.mark.rules
class TestRulesCRUD:
    """Tests for creating, reading, updating, and deleting rules.

    Note: Creating rules requires Pro subscription. These tests may fail
    for free-tier test users.
    """

    @allure.story("Create Recurring Expense Rule")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.skip(reason="Requires Pro subscription")
    def test_create_recurring_expense_rule(self, pages: Pages, personal_ledger: dict):
        """Test creating a recurring expense rule."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])

        with allure.step("Create a new recurring rule"):
            pom.create_recurring_rule(
                title="Monthly Subscription",
                amount="299",
                category="shopping",
                rule_type="expense",
            )

        with allure.step("Verify rule was created"):
            # After creation, empty state should be gone
            pom.wait(500)  # Wait for UI update
            # Note: We may need to check for rule card or success toast
            pom.screenshot("rule_created")

    @allure.story("Create Recurring Income Rule")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.skip(reason="Requires Pro subscription")
    def test_create_recurring_income_rule(self, pages: Pages, personal_ledger: dict):
        """Test creating a recurring income rule."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])

        with allure.step("Open add dialog and select income"):
            pom.click_add_recurring()
            pom.select_type("income")

        with allure.step("Fill rule details"):
            pom.fill_title("Monthly Salary")
            pom.fill_amount("50000")

        with allure.step("Submit rule"):
            pom.submit_rule()

        pom.screenshot("income_rule_created")


@allure.parent_suite("E2E Tests")
@allure.suite("Rules")
@allure.epic("Group Management")
@allure.feature("Add Repayment")
@pytest.mark.rules
class TestRepaymentRules:
    """Tests for repayment rules feature."""

    @allure.story("Add Repayment Dialog Opens")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_repayment_dialog_opens(self, pages: Pages, personal_ledger: dict):
        """Test that clicking add repayment opens the dialog."""
        pom = pages.rules
        pom.open_rules(personal_ledger["id"])

        with allure.step("Click add repayment button"):
            pom.click_add_repayment()

        with allure.step("Verify dialog is visible"):
            pom.expect_visible(pom.DIALOG)

        pom.screenshot("add_repayment_dialog")

        with allure.step("Close dialog"):
            pom.cancel_rule()
