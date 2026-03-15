import contextlib

import allure
import pytest

from api.transaction import TransactionAPI
from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Transactions")
@allure.epic("Transaction Management")
@allure.feature("Transaction CRUD")
@pytest.mark.transactions
class TestTransactionCRUD:
    PERSONAL_GROUP_ID = ""
    EXPENSE_ID = ""
    INCOME_ID = ""
    TRANSFER_ID = ""

    def test_setup(self, personal_ledger: dict):
        TestTransactionCRUD.PERSONAL_GROUP_ID = personal_ledger["id"]

    @allure.story("Create Expense")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_expense(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        res = pom.create_transaction(
            title="Lunch", amount="350", t_type="expense", note="Team lunch"
        )
        assert res, "Transaction response should not be empty"
        TestTransactionCRUD.EXPENSE_ID = res["id"]
        pom.expect_visible(pom.get_transaction_card(res["id"]))

    @allure.story("Create Income")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_income(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        res = pom.create_transaction(title="Salary", amount="50000", t_type="income")
        assert res, "Transaction response should not be empty"
        TestTransactionCRUD.INCOME_ID = res["id"]
        pom.expect_visible(pom.get_transaction_card(res["id"]))

    @allure.story("Create Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_transfer(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.click(pom.ADD_TRANSACTION_BTN)
        pom.wait(300)
        if not pom.is_visible(pom.TYPE_TAB["transfer"]):
            pytest.skip("Transfer tab not available on personal ledger")
        pom.click(pom.CANCEL_BTN)
        res = pom.create_transaction(title="Reimburse", amount="200", t_type="transfer")
        assert res, "Transaction response should not be empty"
        TestTransactionCRUD.TRANSFER_ID = res["id"]
        pom.expect_visible(pom.get_transaction_card(res["id"]))

    @allure.story("Open Transaction Detail")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_open_transaction_detail(self, pages: Pages):
        if not self.EXPENSE_ID:
            pytest.skip("No expense transaction created")
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.open_transaction(self.EXPENSE_ID).wait_for_loaded()
        pom.expect_url_contains(f"/transaction/{self.EXPENSE_ID}")
        pom.screenshot("transaction_detail")

    @allure.story("Filter Expense Only")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_expense_only(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.filter_by_type("expense")
        pom.wait(500)
        if self.EXPENSE_ID:
            pom.expect_visible(pom.get_transaction_card(self.EXPENSE_ID))

    @allure.story("Filter Income Only")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_income_only(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.filter_by_type("income")
        pom.wait(500)
        if self.INCOME_ID:
            pom.expect_visible(pom.get_transaction_card(self.INCOME_ID))

    @allure.story("Filter All")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_all(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.filter_by_type("all")
        pom.wait(500)
        if self.EXPENSE_ID:
            pom.expect_visible(pom.get_transaction_card(self.EXPENSE_ID))
        if self.INCOME_ID:
            pom.expect_visible(pom.get_transaction_card(self.INCOME_ID))

    @allure.story("Search Transaction")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_transaction(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.search_transaction("Lunch")
        pom.wait(500)
        if self.EXPENSE_ID:
            pom.expect_visible(pom.get_transaction_card(self.EXPENSE_ID))

    @allure.story("Switch to Calendar View")
    @allure.severity(allure.severity_level.NORMAL)
    def test_switch_view_calendar(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.switch_view("calendar")
        pom.wait(500)
        pom.screenshot("calendar_view")

    @allure.story("Switch to List View")
    @allure.severity(allure.severity_level.NORMAL)
    def test_switch_view_list(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        pom.switch_view("list")
        pom.wait(500)
        pom.screenshot("list_view")

    @allure.story("Cleanup Transactions")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cleanup(self, transaction_api: TransactionAPI):
        for tid in [self.EXPENSE_ID, self.INCOME_ID, self.TRANSFER_ID]:
            if tid:
                with contextlib.suppress(Exception):
                    transaction_api.delete_transaction(tid)
