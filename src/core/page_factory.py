from typing import TypeVar

from playwright.sync_api import Page

from core.logger import logger

T = TypeVar("T")


class PageFactory:
    """Factory for creating Page Objects with dependency injection."""

    _page_cache: dict[str, object] = {}

    def __init__(self, page: Page):
        self.page = page
        self._page_cache = {}

    def get_page(self, page_class: type[T]) -> T:
        class_name = page_class.__name__

        if class_name not in self._page_cache:
            logger.debug(f"Creating new instance of {class_name}")
            self._page_cache[class_name] = page_class(self.page)

        return self._page_cache[class_name]

    def clear_cache(self):
        self._page_cache.clear()


class Pages:
    def __init__(self, page: Page):
        self._factory = PageFactory(page)
        self._page = page

    # ==============================================================
    # Page Objects
    # ==============================================================

    @property
    def base(self):
        from pages.base_page import BasePage

        return self._factory.get_page(BasePage)

    @property
    def login(self):
        from pages.login_page import LoginPage

        return self._factory.get_page(LoginPage)

    @property
    def groups(self):
        from pages.groups_page import GroupsPage

        return self._factory.get_page(GroupsPage)

    @property
    def group_detail(self):
        from pages.group_detail_page import GroupDetailPage

        return self._factory.get_page(GroupDetailPage)

    @property
    def profile(self):
        from pages.profile_page import ProfilePage

        return self._factory.get_page(ProfilePage)

    @property
    def balance(self):
        from pages.balance_page import BalancePage

        return self._factory.get_page(BalancePage)

    @property
    def group_settings(self):
        from pages.group_settings_page import GroupSettingsPage

        return self._factory.get_page(GroupSettingsPage)

    @property
    def rules(self):
        from pages.rules_page import RulesPage

        return self._factory.get_page(RulesPage)
