from playwright.sync_api import Page

from pages.base_page import BasePage


class ProfilePage(BasePage):
    URL_PATH = "/profile"

    DISPLAY_NAME = "div.flex-1 > h2"
    AVATAR = "[data-testid='avatar'], .avatar img"
    SUBSCRIPTION_STATUS = "[data-testid='subscription']"

    def __init__(self, page: Page):
        super().__init__(page)

    def get_display_name(self) -> str:
        self.page.locator(self.DISPLAY_NAME).first.wait_for(state="visible", timeout=self.timeout)
        return self.page.locator(self.DISPLAY_NAME).first.text_content() or ""

    def is_avatar_visible(self) -> bool:
        return self.is_visible(self.AVATAR)
