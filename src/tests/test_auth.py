import allure
import pytest

from config.settings import settings
from core.logger import logger
from core.page_factory import Pages


@allure.parent_suite("E2E Tests")
@allure.suite("Authentication")
@allure.epic("Authentication")
@allure.feature("New User Authentication")
@pytest.mark.auth
class TestNewUserAuthentication:
    PERSONAL_GROUP_ID = ""

    @allure.story("User Created")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_user_created(self, test_user):
        assert test_user["access_token"], "Test User Created"
        logger.info(f"Test user ready: {test_user['user']['id']}")

    @allure.story("Homepage Load")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_homepage_loads(self, guest_pages: Pages):
        url = guest_pages.login.open().current_url
        guest_pages.login.assertion(url is not None, "Login page loaded")

    @allure.story("Token Auth")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_token_auth_redirects_to_groups(self, pages: Pages):
        pages.groups.open().expect_url_contains("/groups")

    @allure.story("Access Personal Ledger")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_access_personal_ledger(self, pages: Pages):
        title = pages.groups.open().click_personal_group_card().wait_for_loaded().get_header_title()
        pages.groups.assertion(
            settings.TEST_USER_DISPLAY_NAME in title,
            f"Expected '{settings.TEST_USER_DISPLAY_NAME}' in title: {title}",
        )
        TestNewUserAuthentication.PERSONAL_GROUP_ID = pages.groups.current_url.split("/")[-1]

    @allure.story("Logout Redirects to Login")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_logout_redirects_to_login(self, pages: Pages):
        pages.groups.open().wait_for_loaded()
        pages.groups.logout()
        pages.groups.wait_for_loaded()
        pages.groups.expect_url_contains("/")


@allure.parent_suite("E2E Tests")
@allure.suite("Authentication")
@allure.epic("Authentication")
@allure.feature("Old User Authentication")
@pytest.mark.auth
class TestOldUserAuthentication:
    @allure.story("Old User Exists")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_old_user_exists(self, old_user):
        assert old_user["access_token"], "Old User has access_token"
        logger.info(f"Old user ready: {old_user['user']['id']}")

    @allure.story("Old User Redirects to Groups")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_old_user_redirects_to_groups(self, old_user_pages: Pages):
        old_user_pages.groups.open().expect_url_contains("/groups")

    @allure.story("Old User Has Personal Ledger")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_old_user_has_personal_ledger(self, old_user_pages: Pages):
        old_user_pages.groups.open().wait_for_loaded()
        old_user_pages.groups.expect_visible(old_user_pages.groups.PERSONAL_GROUP_CARD)
