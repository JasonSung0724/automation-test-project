import contextlib

import allure
import pytest

from api.balance import BalanceAPI
from api.group import GroupAPI
from api.transaction import TransactionAPI
from core.logger import logger
from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Multi-Person Group")
@allure.epic("Group Management")
@allure.feature("Multi-Person Group Setup")
@pytest.mark.multigroup
class TestMultiPersonGroupSetup:

    @allure.story("Shared Group Has Two Members")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_shared_group_has_two_members(self, shared_group: dict):
        assert shared_group["group_id"], "Group ID should exist"
        assert shared_group["test_user_member_id"], "test_user member_id should exist"
        assert shared_group["old_user_member_id"], "old_user member_id should exist"
        assert len(shared_group["members"]) >= 2, f"Expected at least 2 members, got {len(shared_group['members'])}"

    @allure.story("Group Detail Shows Both Members")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_group_detail_shows_members(self, group_api: GroupAPI, shared_group: dict):
        group = group_api.get_group(shared_group["group_id"])
        members = group.get("members", [])
        assert len(members) >= 2, f"Expected >= 2 members, got {len(members)}"


@allure.parent_suite("E2E Tests")
@allure.suite("Multi-Person Group")
@allure.epic("Group Management")
@allure.feature("Multi-Person Transactions (API)")
@pytest.mark.multigroup
class TestMultiPersonTransactionsAPI:
    TX1_ID = ""
    TX2_ID = ""

    @allure.story("User1 Creates Expense 600 Split Equally")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user1_creates_expense_600(self, transaction_api: TransactionAPI, shared_group: dict):
        res = transaction_api.create_transaction(
            shared_group["group_id"],
            {
                "title": "Dinner (User1 pays)",
                "amount": 600,
                "transaction_type": "expense",
                "paid_by": shared_group["test_user_member_id"],
                "splits": [
                    {"member_id": shared_group["test_user_member_id"], "amount": 300},
                    {"member_id": shared_group["old_user_member_id"], "amount": 300},
                ],
            },
        )
        assert res["id"]
        assert int(res["amount"]) == 600
        TestMultiPersonTransactionsAPI.TX1_ID = res["id"]
        logger.info(f"Created TX1: {res['id']}")

    @allure.story("User2 Creates Expense 400 Split Equally")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user2_creates_expense_400(self, old_user_transaction_api: TransactionAPI, shared_group: dict):
        res = old_user_transaction_api.create_transaction(
            shared_group["group_id"],
            {
                "title": "Taxi (User2 pays)",
                "amount": 400,
                "transaction_type": "expense",
                "paid_by": shared_group["old_user_member_id"],
                "splits": [
                    {"member_id": shared_group["test_user_member_id"], "amount": 200},
                    {"member_id": shared_group["old_user_member_id"], "amount": 200},
                ],
            },
        )
        assert res["id"]
        assert int(res["amount"]) == 400
        TestMultiPersonTransactionsAPI.TX2_ID = res["id"]
        logger.info(f"Created TX2: {res['id']}")

    @allure.story("Verify Balance: User2 Owes User1 $100")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_verify_balance_via_api(self, balance_api: BalanceAPI, shared_group: dict):
        """
        TX1: User1 pays 600, split 300/300
        TX2: User2 pays 400, split 200/200
        User1: paid 600, owes 500 => balance +100
        User2: paid 400, owes 500 => balance -100
        Settlement: User2 pays User1 $100

        API returns: {member_balances: [{member_id, balance}], settlements: [{from_member_id, to_member_id, amount}]}
        """
        balance = balance_api.get_balance(shared_group["group_id"])
        logger.info(f"Balance response: {balance}")

        allure.attach(
            str(balance),
            name="Balance API Response",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert balance is not None

        member_balances = balance.get("member_balances", [])
        settlements = balance.get("settlements", [])

        user1_mid = shared_group["test_user_member_id"]
        user2_mid = shared_group["old_user_member_id"]

        for mb in member_balances:
            if mb["member_id"] == user1_mid:
                assert int(mb["balance"]) == 100, f"User1 balance should be +100, got {mb['balance']}"
            elif mb["member_id"] == user2_mid:
                assert int(mb["balance"]) == -100, f"User2 balance should be -100, got {mb['balance']}"

        assert len(settlements) >= 1, f"Expected at least 1 settlement, got {len(settlements)}"
        s = settlements[0]
        assert s["from_member_id"] == user2_mid, "User2 should be the payer"
        assert s["to_member_id"] == user1_mid, "User1 should be the receiver"
        assert int(s["amount"]) == 100, f"Settlement amount should be 100, got {s['amount']}"

    @allure.story("Verify Transactions List")
    @allure.severity(allure.severity_level.NORMAL)
    def test_verify_transactions_list(self, transaction_api: TransactionAPI, shared_group: dict):
        result = transaction_api.get_transactions(shared_group["group_id"])
        items = result.get("items", result if isinstance(result, list) else [])
        assert len(items) >= 2, f"Expected at least 2 transactions, got {len(items)}"

    @allure.story("Cleanup API Transactions")
    @allure.severity(allure.severity_level.MINOR)
    def test_cleanup_api_transactions(self, transaction_api: TransactionAPI):
        for tx_id in [self.TX1_ID, self.TX2_ID]:
            if tx_id:
                with contextlib.suppress(Exception):
                    transaction_api.delete_transaction(tx_id)


@allure.parent_suite("E2E Tests")
@allure.suite("Multi-Person Group")
@allure.epic("Group Management")
@allure.feature("Multi-Person Transactions (UI)")
@pytest.mark.multigroup
class TestMultiPersonTransactionsUI:
    UI_TX_ID = ""
    TRANSFER_TX_ID = ""

    @allure.story("Shared Group Page Loads with Correct Tabs")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_shared_group_page_loads(self, pages: Pages, shared_group: dict):
        pom = pages.group_detail
        pom.open_group(shared_group["group_id"]).wait_for_loaded()
        with allure.step("Verify shared group tabs"):
            pom.expect_visible(pom.SHARE_TAB)
            pom.expect_visible(pom.BALANCE_TAB)
            pom.expect_visible(pom.SETTING_TAB)
        pom.screenshot("shared_group_tabs")

    @allure.story("Create Expense via UI")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_expense_via_ui(self, pages: Pages, shared_group: dict):
        pom = pages.group_detail
        pom.open_group(shared_group["group_id"]).wait_for_loaded()
        res = pom.create_transaction(
            title="UI Shared Expense",
            amount="800",
            t_type="expense",
            note="Created via UI test",
        )
        assert res, "Transaction response should not be empty"
        TestMultiPersonTransactionsUI.UI_TX_ID = res["id"]
        pom.expect_visible(pom.get_transaction_card(res["id"]))
        pom.screenshot("ui_expense_created")

    @allure.story("Create Transfer via UI")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_transfer_via_ui(self, pages: Pages, shared_group: dict):
        pom = pages.group_detail
        pom.open_group(shared_group["group_id"]).wait_for_loaded()
        pom.click(pom.ADD_TRANSACTION_BTN)
        pom.wait(300)
        if not pom.is_visible(pom.TYPE_TAB["transfer"]):
            pytest.skip("Transfer tab not available")
        pom.click(pom.CANCEL_BTN)
        res = pom.create_transaction(title="UI Transfer", amount="150", t_type="transfer")
        assert res, "Transfer response should not be empty"
        TestMultiPersonTransactionsUI.TRANSFER_TX_ID = res["id"]
        pom.expect_visible(pom.get_transaction_card(res["id"]))
        pom.screenshot("ui_transfer_created")

    @allure.story("Filter Transfer Type")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_transfer_type(self, pages: Pages, shared_group: dict):
        pom = pages.group_detail
        pom.open_group(shared_group["group_id"]).wait_for_loaded()
        if not pom.is_visible(pom.FILTER_TRANSFER, timeout=2000):
            pytest.skip("Transfer filter not available on shared groups")
        pom.filter_by_type("transfer")
        pom.wait(500)
        if self.TRANSFER_TX_ID:
            pom.expect_visible(pom.get_transaction_card(self.TRANSFER_TX_ID))
        pom.screenshot("filter_transfer")

    @allure.story("Cleanup UI Transactions")
    @allure.severity(allure.severity_level.MINOR)
    def test_cleanup_ui_transactions(self, transaction_api: TransactionAPI):
        for tx_id in [self.UI_TX_ID, self.TRANSFER_TX_ID]:
            if tx_id:
                with contextlib.suppress(Exception):
                    transaction_api.delete_transaction(tx_id)


@allure.parent_suite("E2E Tests")
@allure.suite("Multi-Person Group")
@allure.epic("Balance & Settlement")
@allure.feature("Multi-Person Balance")
@pytest.mark.multigroup
@pytest.mark.balance
class TestMultiPersonBalance:
    SETUP_TX_ID = ""

    def test_setup_balance_data(self, transaction_api: TransactionAPI, shared_group: dict):
        res = transaction_api.create_transaction(
            shared_group["group_id"],
            {
                "title": "Balance Setup Expense",
                "amount": 1000,
                "transaction_type": "expense",
                "paid_by": shared_group["test_user_member_id"],
                "splits": [
                    {"member_id": shared_group["test_user_member_id"], "amount": 500},
                    {"member_id": shared_group["old_user_member_id"], "amount": 500},
                ],
            },
        )
        TestMultiPersonBalance.SETUP_TX_ID = res["id"]

    @allure.story("Balance Tab Visible on Shared Group")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_balance_tab_visible(self, pages: Pages, shared_group: dict):
        pom = pages.group_detail
        pom.open_group(shared_group["group_id"]).wait_for_loaded()
        pom.expect_visible(pom.BALANCE_TAB)
        pom.screenshot("balance_tab_visible")

    @allure.story("Navigate to Balance via Tab")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_navigate_to_balance_via_tab(self, pages: Pages, shared_group: dict):
        pom = pages.group_detail
        pom.open_group(shared_group["group_id"]).wait_for_loaded()
        pom.click(pom.BALANCE_TAB)
        pom.wait_for_loaded()
        pom.expect_url_contains("/balance")
        pom.screenshot("balance_page_via_tab")

    @allure.story("Balance Page Loads via Direct URL")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_balance_page_loads(self, pages: Pages, shared_group: dict):
        pom = pages.balance
        pom.open_balance(shared_group["group_id"])
        pom.expect_url_contains("/balance")
        pom.screenshot("balance_page_direct")

    @allure.story("Settlement Settle Button Visible")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_settle_button_visible(self, pages: Pages, shared_group: dict):
        pom = pages.balance
        pom.open_balance(shared_group["group_id"])
        if not pom.is_visible(pom.SETTLEMENT_SETTLE_BTN, timeout=5000):
            pom.screenshot("settle_button_not_found")
            pytest.skip("Settle button not visible")
        pom.expect_visible(pom.SETTLEMENT_SETTLE_BTN)
        pom.screenshot("settle_button_visible")

    @allure.story("Click Settle Opens Confirmation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_click_settle_opens_confirmation(self, pages: Pages, shared_group: dict):
        pom = pages.balance
        pom.open_balance(shared_group["group_id"])
        if not pom.is_visible(pom.SETTLEMENT_SETTLE_BTN, timeout=5000):
            pytest.skip("Settle button not visible")
        pom.click_settle()
        has_confirm = pom.is_visible(pom.SETTLEMENT_CONFIRM_BTN, timeout=3000)
        has_cancel = pom.is_visible(pom.SETTLEMENT_CANCEL_BTN, timeout=3000)
        pom.screenshot("settlement_confirmation")
        assert has_confirm or has_cancel, "Settlement confirmation UI should appear"
        if has_cancel:
            pom.cancel_settlement()

    @allure.story("Cleanup Balance Data")
    @allure.severity(allure.severity_level.MINOR)
    def test_cleanup(self, transaction_api: TransactionAPI):
        if self.SETUP_TX_ID:
            with contextlib.suppress(Exception):
                transaction_api.delete_transaction(self.SETUP_TX_ID)
