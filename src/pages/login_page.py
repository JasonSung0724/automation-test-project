from playwright.sync_api import Page

from api.user import UserAPI
from core.decorators import step
from core.logger import logger
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL_PATH = "/"

    LINE_LOGIN_BTN = "button:has-text('LINE')"
    GOOGLE_LOGIN_BTN = "button:has-text('Google')"
    DEMO_LOGIN_BTN = "button:has-text('Demo'), button:has-text('Experience')"

    def __init__(self, page: Page):
        super().__init__(page)

    @step("Click LINE login")
    def click_line_login(self):
        return self.click(self.LINE_LOGIN_BTN)

    @step("Click Google login")
    def click_google_login(self):
        return self.click(self.GOOGLE_LOGIN_BTN)

    @step("Click demo login")
    def click_demo_login(self):
        return self.click(self.DEMO_LOGIN_BTN)

    def is_login_page(self) -> bool:
        return self.is_visible(self.LINE_LOGIN_BTN) or self.is_visible(self.GOOGLE_LOGIN_BTN)

    @step("Create new user")
    def create_new_user(self) -> dict[str, str]:
        """
        {
            "access_token": "",
            "token_type": "bearer",
            "expires_at": "",
            "user": {
                "id": "f0a67a1f-9b10-4d7b-80a7-49a8a4cbdb2c",
                "provider_user_id": "test_5af22708ac34",
                "display_name": "E2E Debug",
                "picture_url": null,
                "user_type": "normal",
                "oauth_display_name": ""
            },
            "redirect_path": null
        }
        """
        user_api = UserAPI()
        logger.info("Creating new user")
        return user_api.create_test_user()

    @step("Delete user")
    def delete_user(self, user_id: str) -> dict[str, str]:
        user_api = UserAPI()
        logger.info(f"Deleting user: {user_id}")
        return user_api.delete_test_user(user_id)
