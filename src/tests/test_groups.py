import allure
import pytest

from api.group import GroupAPI
from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Groups")
@allure.epic("Group Management")
@allure.feature("Personal Group")
@pytest.mark.groups
class TestPersonalGroup:
    PERSONAL_GROUP_ID = ""

    def test_setup_class(self, personal_ledger: dict):
        TestPersonalGroup.PERSONAL_GROUP_ID = personal_ledger["id"]

    @allure.story("Access Personal Ledger by URL")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_access_personal_ledger_by_url(self, pages: Pages):
        pom = pages.group_detail
        pom.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        with allure.step("Check tabs exist"):
            pom.expect_not_exist(pom.SHARE_TAB)
            pom.expect_not_exist(pom.PERSONAL_LEDGER_TAB)
            pom.expect_not_exist(pom.BALANCE_TAB)
            pom.expect_visible(pom.SETTING_TAB)
            pom.expect_visible(pom.RULE_TAB)
            pom.expect_visible(pom.STATS_TAB)
            pom.expect_visible(pom.BUDGET_TAB)
            pom.expect_visible(pom.IMPORT_TAB)
            pom.expect_visible(pom.EXPORT_TAB)
        with allure.step("Check filters exist"):
            pom.expect_visible(pom.FILTER_ALL)
            pom.expect_visible(pom.FILTER_INCOME)
            pom.expect_visible(pom.FILTER_EXPENSE)
            pom.expect_visible(pom.FILTER_TRANSFER)
        with allure.step("Check view types exist"):
            pom.expect_visible(pom.VIEW_LIST)
            pom.expect_visible(pom.VIEW_CALENDAR)
            pom.expect_visible(pom.VIEW_LOGS)
        pom.expect_visible(pom.ADD_TRANSACTION_BTN)

    @allure.story("Create Expense Transaction")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_expense_transaction(self, pages: Pages):
        pages.group_detail.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        res = pages.group_detail.create_transaction(
            title="E2E Expense",
            amount="1000",
            t_type="expense",
            note="Expense test",
        )
        assert res, "Transaction response should not be empty"
        transaction_id = res["id"]
        card_selector = pages.group_detail.get_transaction_card(transaction_id)
        pages.group_detail.expect_visible(card_selector)

    @allure.story("Create Income Transaction")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_income_transaction(self, pages: Pages):
        pages.group_detail.open_group(self.PERSONAL_GROUP_ID).wait_for_loaded()
        res = pages.group_detail.create_transaction(
            title="E2E Income",
            amount="5000",
            t_type="income",
        )
        assert res, "Transaction response should not be empty"
        card_selector = pages.group_detail.get_transaction_card(res["id"])
        pages.group_detail.expect_visible(card_selector)


@allure.parent_suite("E2E Tests")
@allure.suite("Groups")
@allure.epic("Group Management")
@allure.feature("Group CRUD")
@pytest.mark.groups
class TestGroupCRUD:
    CREATED_GROUP_ID = ""

    @allure.story("Create Group via UI")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_group_via_ui(self, pages: Pages):
        pom = pages.groups
        with pages.groups.page.expect_response(
            lambda resp: "/api/groups" in resp.url and resp.request.method == "POST"
        ) as response_info:
            pom.open().wait_for_loaded()
            pom.create_group("E2E Test Group")
        res = response_info.value
        if res.status == 201:
            data = res.json()
            TestGroupCRUD.CREATED_GROUP_ID = data["id"]
        assert self.CREATED_GROUP_ID, "Group creation should return an ID"
        pom.wait_for_loaded()
        pom.expect_visible(f"[data-testid='group-card-{self.CREATED_GROUP_ID}']")

    @allure.story("Created Group Visible in List")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_created_group_in_list(self, pages: Pages):
        if not self.CREATED_GROUP_ID:
            pytest.skip("No group created")
        pages.groups.open().wait_for_loaded()
        pages.groups.expect_visible(f"[data-testid='group-card-{self.CREATED_GROUP_ID}']")

    @allure.story("Search Group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_group(self, pages: Pages):
        pages.groups.open().wait_for_loaded()
        pages.groups.search_group("E2E Test")
        pages.groups.wait(500)
        count = pages.groups.get_group_count()
        pages.groups.assertion(count >= 1, f"Expected at least 1 group, found {count}")

    @allure.story("Search Nonexistent Group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_nonexistent_group(self, pages: Pages):
        pages.groups.open().wait_for_loaded()
        pages.groups.search_group("ZZZZZ_NOT_EXIST_12345")
        pages.groups.wait(500)
        count = pages.groups.get_group_count()
        pages.groups.assertion(count == 0, f"Expected 0 groups, found {count}")

    @allure.story("Delete Group via API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_group_via_api(self, group_api: GroupAPI):
        if not self.CREATED_GROUP_ID:
            pytest.skip("No group to delete")
        group_api.delete_group(self.CREATED_GROUP_ID)
