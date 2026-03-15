import contextlib

import allure
import pytest

from api.transaction import TransactionAPI
from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Balance")
@allure.epic("Balance & Settlement")
@allure.feature("Balance")
@pytest.mark.balance
class TestBalance:
    PERSONAL_GROUP_ID = ""
    TRANSACTION_ID = ""

    def test_setup(self, personal_ledger: dict, transaction_api: TransactionAPI):
        TestBalance.PERSONAL_GROUP_ID = personal_ledger["id"]
        member_id = personal_ledger["member_id"]
        res = transaction_api.create_transaction(
            self.PERSONAL_GROUP_ID,
            {
                "title": "Balance Test Expense",
                "amount": 500,
                "transaction_type": "expense",
                "paid_by": member_id,
                "splits": [{"member_id": member_id, "amount": 500}],
            },
        )
        TestBalance.TRANSACTION_ID = res["id"]

    @allure.story("Navigate to Balance via Tab")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_navigate_to_balance_via_tab(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        if not pom.is_visible(pom.BALANCE_TAB, timeout=3000):
            pytest.skip("Balance tab not available on personal ledger")
        pom.click(pom.BALANCE_TAB)
        pom.wait_for_loaded()
        pom.expect_url_contains("/balance")

    @allure.story("Balance Page Loads")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_balance_page_loads(self, pages: Pages):
        pom = pages.balance
        pom.open_balance(self.PERSONAL_GROUP_ID)
        pom.expect_url_contains("/balance")
        pom.screenshot("balance_page")

    @allure.story("Cleanup")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cleanup(self, transaction_api: TransactionAPI):
        if self.TRANSACTION_ID:
            with contextlib.suppress(Exception):
                transaction_api.delete_transaction(self.TRANSACTION_ID)
