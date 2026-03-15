import allure
import pytest

from api.balance import BalanceAPI
from api.category import CategoryAPI
from api.group import GroupAPI
from api.transaction import TransactionAPI
from api.user import UserAPI


@allure.parent_suite("API Tests")
@allure.suite("API")
@allure.epic("API Validation")
@allure.feature("User API")
@pytest.mark.api
class TestUserAPI:
    @allure.story("Get Current User")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_get_current_user(self, test_user: dict):
        api = UserAPI(test_user["access_token"])
        user = api.get_me()
        assert user["id"] == test_user["user"]["id"]
        assert user["display_name"] == test_user["user"]["display_name"]

    @allure.story("Create and Delete User")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_and_delete_user(self):
        api = UserAPI()
        user_info = api.create_test_user("API Test User")
        assert user_info["access_token"]
        assert user_info["user"]["id"]
        api.delete_test_user(user_info["user"]["id"])


@allure.parent_suite("API Tests")
@allure.suite("API")
@allure.epic("API Validation")
@allure.feature("Group API")
@pytest.mark.api
class TestGroupAPI:
    GROUP_ID = ""

    @allure.story("Create Group")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_group(self, group_api: GroupAPI):
        res = group_api.create_group("API Test Group")
        assert res["id"]
        assert res["name"] == "API Test Group"
        TestGroupAPI.GROUP_ID = res["id"]

    @allure.story("Get Groups")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_groups(self, group_api: GroupAPI):
        groups = group_api.get_groups()
        assert isinstance(groups, list)
        assert len(groups) >= 1

    @allure.story("Get Personal Ledger")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_personal_ledger(self, personal_ledger: dict):
        assert personal_ledger["id"]
        assert personal_ledger["member_id"]

    @allure.story("Get Group Detail")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_group_detail(self, group_api: GroupAPI):
        if not self.GROUP_ID:
            pytest.skip("No group created")
        group = group_api.get_group(self.GROUP_ID)
        assert group["id"] == self.GROUP_ID
        assert group["name"] == "API Test Group"

    @allure.story("Delete Group")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_group(self, group_api: GroupAPI):
        if not self.GROUP_ID:
            pytest.skip("No group to delete")
        group_api.delete_group(self.GROUP_ID)


@allure.parent_suite("API Tests")
@allure.suite("API")
@allure.epic("API Validation")
@allure.feature("Transaction API")
@pytest.mark.api
class TestTransactionAPI:
    TRANSACTION_ID = ""

    @allure.story("Create Transaction")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_transaction(self, transaction_api: TransactionAPI, personal_ledger: dict):
        res = transaction_api.create_transaction(
            personal_ledger["id"],
            {
                "title": "API Test Transaction",
                "amount": 999,
                "transaction_type": "expense",
                "paid_by": personal_ledger["member_id"],
                "splits": [{"member_id": personal_ledger["member_id"], "amount": 999}],
            },
        )
        assert res["id"]
        assert res["title"] == "API Test Transaction"
        TestTransactionAPI.TRANSACTION_ID = res["id"]

    @allure.story("Get Transactions")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_transactions(self, transaction_api: TransactionAPI, personal_ledger: dict):
        result = transaction_api.get_transactions(personal_ledger["id"])
        transactions = result.get("items", [])
        assert len(transactions) >= 1

    @allure.story("Get Transaction Detail")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_transaction_detail(self, transaction_api: TransactionAPI):
        if not self.TRANSACTION_ID:
            pytest.skip("No transaction created")
        tx = transaction_api.get_transaction(self.TRANSACTION_ID)
        assert tx["id"] == self.TRANSACTION_ID
        assert tx["title"] == "API Test Transaction"

    @allure.story("Update Transaction")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_transaction(self, transaction_api: TransactionAPI):
        if not self.TRANSACTION_ID:
            pytest.skip("No transaction created")
        res = transaction_api.update_transaction(
            self.TRANSACTION_ID,
            {"title": "Updated API Transaction", "amount": 1500},
        )
        assert res["title"] == "Updated API Transaction"

    @allure.story("Delete Transaction")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_transaction(self, transaction_api: TransactionAPI):
        if not self.TRANSACTION_ID:
            pytest.skip("No transaction to delete")
        transaction_api.delete_transaction(self.TRANSACTION_ID)


@allure.parent_suite("API Tests")
@allure.suite("API")
@allure.epic("API Validation")
@allure.feature("Balance API")
@pytest.mark.api
class TestBalanceAPI:
    @allure.story("Get Balance")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_balance(self, test_user: dict, personal_ledger: dict):
        balance = BalanceAPI(test_user["access_token"]).get_balance(personal_ledger["id"])
        assert balance is not None

    @allure.story("Get Stats")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_stats(self, test_user: dict, personal_ledger: dict):
        stats = BalanceAPI(test_user["access_token"]).get_stats(personal_ledger["id"])
        assert stats is not None


@allure.parent_suite("API Tests")
@allure.suite("API")
@allure.epic("API Validation")
@allure.feature("Category API")
@pytest.mark.api
class TestCategoryAPI:
    @allure.story("Get Preset Categories")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_preset_categories(self, test_user: dict):
        api = CategoryAPI(test_user["access_token"])
        categories = api.get_preset_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0

    @allure.story("Get Group Categories")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_group_categories(self, test_user: dict, personal_ledger: dict):
        categories = CategoryAPI(test_user["access_token"]).get_categories(personal_ledger["id"])
        assert isinstance(categories, list)
