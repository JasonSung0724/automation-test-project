import contextlib

import allure
import pytest

from api.group import GroupAPI
from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Settings")
@allure.epic("Group Settings")
@allure.feature("Group Settings")
@pytest.mark.settings
class TestGroupSettings:
    GROUP_ID = ""

    def test_setup(self, group_api: GroupAPI):
        res = group_api.create_group("E2E Settings Group")
        TestGroupSettings.GROUP_ID = res["id"]

    @allure.story("Navigate to Settings")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_navigate_to_settings(self, pages: Pages):
        if not self.GROUP_ID:
            pytest.skip("No group created")
        pom = pages.group_detail
        pom.open_group(self.GROUP_ID).wait_for_loaded()
        pom.click(pom.SETTING_TAB)
        pom.wait_for_loaded()
        pom.expect_url_contains("/settings")

    @allure.story("Settings Page Loads")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_settings_page_loads(self, pages: Pages):
        if not self.GROUP_ID:
            pytest.skip("No group created")
        pom = pages.group_settings
        pom.open_settings(self.GROUP_ID)
        pom.expect_url_contains("/settings")
        pom.screenshot("settings_page")

    @allure.story("Navigate to Members")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_navigate_to_members(self, pages: Pages):
        if not self.GROUP_ID:
            pytest.skip("No group created")
        pom = pages.group_settings
        pom.open_members(self.GROUP_ID)
        pom.expect_url_contains("/members")
        pom.screenshot("members_page")

    @allure.story("Cleanup")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cleanup(self, group_api: GroupAPI):
        if self.GROUP_ID:
            with contextlib.suppress(Exception):
                group_api.delete_group(self.GROUP_ID)
