import allure
import pytest

from config.settings import settings
from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Profile")
@allure.epic("User Profile")
@allure.feature("New User Profile")
@pytest.mark.profile
class TestNewUserProfile:
    @allure.story("Navigate to Profile")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_navigate_to_profile(self, pages: Pages):
        pages.groups.open().wait_for_loaded()
        pages.groups.goto_profile()
        pages.profile.wait_for_loaded()
        pages.profile.expect_url_contains("/profile")

    @allure.story("Display Name Visible")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_display_name_visible(self, pages: Pages):
        pages.profile.open().wait_for_loaded()
        name = pages.profile.get_display_name()
        pages.profile.assertion(
            settings.TEST_USER_DISPLAY_NAME in name,
            f"Expected '{settings.TEST_USER_DISPLAY_NAME}' in '{name}'",
        )


@allure.parent_suite("E2E Tests")
@allure.suite("Profile")
@allure.epic("User Profile")
@allure.feature("Old User Profile")
@pytest.mark.profile
class TestOldUserProfile:
    @allure.story("Old User Profile Loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_old_user_profile_loads(self, old_user_pages: Pages, old_user: dict):
        old_user_pages.profile.open().wait_for_loaded()
        old_user_pages.profile.expect_url_contains("/profile")
        name = old_user_pages.profile.get_display_name()
        expected = old_user["user"]["display_name"]
        old_user_pages.profile.assertion(
            expected in name,
            f"Expected '{expected}' in '{name}'",
        )
