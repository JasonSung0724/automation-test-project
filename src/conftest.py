import contextlib
import json
from collections.abc import Generator

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from api.balance import BalanceAPI
from api.group import GroupAPI
from api.transaction import TransactionAPI
from api.user import UserAPI
from config.settings import settings
from core.logger import logger
from core.page_factory import Pages

# ============================================================
# Context Factories
# ============================================================


def create_auth_context(browser: Browser, user_data: dict) -> BrowserContext:
    auth_data = json.dumps(
        {
            "mr_splitter_jwt_token": user_data["access_token"],
            "mr_splitter_token_expires": user_data.get("expires_at", ""),
            "mr_splitter_user": user_data["user"],
            "mr_splitter_profile": {
                "userId": user_data["user"]["id"],
                "displayName": user_data["user"]["display_name"],
                "pictureUrl": user_data["user"].get("picture_url"),
            },
        }
    )

    ctx = browser.new_context(
        viewport={
            "width": settings.VIEWPORT_WIDTH,
            "height": settings.VIEWPORT_HEIGHT,
        },
        locale=settings.LOCALE,
    )
    ctx.add_init_script(
        f"""
        const authData = {auth_data};
        Object.entries(authData).forEach(([key, value]) => {{
            window.localStorage.setItem(key, JSON.stringify(value));
        }});
    """
    )
    return ctx


def create_guest_context(browser: Browser) -> BrowserContext:
    return browser.new_context(
        viewport={
            "width": settings.VIEWPORT_WIDTH,
            "height": settings.VIEWPORT_HEIGHT,
        },
        locale=settings.LOCALE,
    )


# ============================================================
# Session Fixtures
# ============================================================


@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    logger.info(f"Launching {settings.BROWSER} browser (headless={settings.HEADLESS})")
    with sync_playwright() as p:
        launcher = getattr(p, settings.BROWSER)
        browser = launcher.launch(
            headless=settings.HEADLESS,
            slow_mo=settings.SLOW_MO,
        )
        yield browser
        browser.close()
        logger.info("Browser closed")


@pytest.fixture(scope="session")
def test_user() -> Generator[dict, None, None]:
    user_info = UserAPI().create_test_user(settings.TEST_USER_DISPLAY_NAME)
    logger.info(f"Created test user: {user_info['user']['id']}")
    yield user_info
    UserAPI().delete_test_user(user_info["user"]["id"])
    logger.info("Deleted test user")


@pytest.fixture(scope="session")
def old_user() -> Generator[dict, None, None]:
    if settings.OLD_USER_TOKEN and settings.OLD_USER_ID:
        logger.info(f"Using existing old user: {settings.OLD_USER_ID}")
        user_api = UserAPI(settings.OLD_USER_TOKEN)
        user_info = user_api.get_me()
        yield {
            "access_token": settings.OLD_USER_TOKEN,
            "expires_at": "",
            "user": user_info,
        }
    else:
        user_info = UserAPI().create_test_user(settings.OLD_USER_DISPLAY_NAME)
        logger.info(f"Created old user: {user_info['user']['id']}")
        logger.info(
            f"To reuse this user, add to .env:\n"
            f"OLD_USER_TOKEN={user_info['access_token']}\n"
            f"OLD_USER_ID={user_info['user']['id']}"
        )
        yield user_info


# ============================================================
# Session API Fixtures
# ============================================================


@pytest.fixture(scope="session")
def group_api(test_user: dict) -> GroupAPI:
    return GroupAPI(test_user["access_token"])


@pytest.fixture(scope="session")
def transaction_api(test_user: dict) -> TransactionAPI:
    return TransactionAPI(test_user["access_token"])


@pytest.fixture(scope="session")
def personal_ledger(group_api: GroupAPI) -> dict:
    return group_api.get_personal_ledger()


# ============================================================
# Session API Fixtures - Old User
# ============================================================


@pytest.fixture(scope="session")
def old_user_group_api(old_user: dict) -> GroupAPI:
    return GroupAPI(old_user["access_token"])


@pytest.fixture(scope="session")
def old_user_transaction_api(old_user: dict) -> TransactionAPI:
    return TransactionAPI(old_user["access_token"])


@pytest.fixture(scope="session")
def balance_api(test_user: dict) -> BalanceAPI:
    return BalanceAPI(test_user["access_token"])


@pytest.fixture(scope="session")
def shared_group(
    group_api: GroupAPI,
    old_user_group_api: GroupAPI,
    test_user: dict,
    old_user: dict,
) -> Generator[dict, None, None]:
    # Step 1: test_user creates group with a virtual member slot
    group = group_api.create_group(
        "E2E Shared Group", currency="TWD", member_names=["Member 2"]
    )
    group_id = group["id"]
    logger.info(f"Created shared group: {group_id}")

    # Step 2: Find test_user's member_id and the virtual slot
    members = group.get("members", [])
    test_user_id = test_user["user"]["id"]
    test_user_member_id = None
    virtual_slot_id = None

    for member in members:
        if member.get("user_id") == test_user_id:
            test_user_member_id = member["id"]
        elif not member.get("user_id") and not member.get("is_line_user"):
            virtual_slot_id = member["id"]

    assert test_user_member_id, f"Cannot find test_user member_id. Members: {members}"
    assert virtual_slot_id, f"Cannot find virtual member slot. Members: {members}"

    # Step 3: old_user joins by binding to the virtual slot
    old_user_group_api.join_group(group_id, member_id=virtual_slot_id)
    logger.info(f"old_user joined group via slot: {virtual_slot_id}")

    # Step 4: Re-fetch group to get updated member data
    group_detail = group_api.get_group(group_id)
    members = group_detail.get("members", [])
    old_user_id = old_user["user"]["id"]
    old_user_member_id = None

    for member in members:
        if member.get("user_id") == old_user_id:
            old_user_member_id = member["id"]

    assert old_user_member_id, f"Cannot find old_user member_id. Members: {members}"

    yield {
        "group_id": group_id,
        "group": group_detail,
        "test_user_member_id": test_user_member_id,
        "old_user_member_id": old_user_member_id,
        "members": members,
    }

    with contextlib.suppress(Exception):
        group_api.delete_group(group_id)
        logger.info(f"Deleted shared group: {group_id}")


# ============================================================
# Function Scope - Authenticated (default, isolated tests)
# ============================================================


@pytest.fixture
def context(browser: Browser, test_user: dict) -> Generator[BrowserContext, None, None]:
    ctx = create_auth_context(browser, test_user)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.fixture
def pages(page: Page) -> Pages:
    return Pages(page)


# ============================================================
# Class Scope - Authenticated (shared page within class)
# ============================================================


@pytest.fixture(scope="class")
def class_context(browser: Browser, test_user: dict) -> Generator[BrowserContext, None, None]:
    ctx = create_auth_context(browser, test_user)
    yield ctx
    ctx.close()


@pytest.fixture(scope="class")
def class_page(class_context: BrowserContext) -> Generator[Page, None, None]:
    pg = class_context.new_page()
    yield pg
    pg.close()


@pytest.fixture(scope="class")
def class_pages(class_page: Page) -> Pages:
    return Pages(class_page)


# ============================================================
# Function Scope - Old User Authenticated
# ============================================================


@pytest.fixture
def old_user_context(browser: Browser, old_user: dict) -> Generator[BrowserContext, None, None]:
    ctx = create_auth_context(browser, old_user)
    yield ctx
    ctx.close()


@pytest.fixture
def old_user_page(old_user_context: BrowserContext) -> Generator[Page, None, None]:
    pg = old_user_context.new_page()
    yield pg
    pg.close()


@pytest.fixture
def old_user_pages(old_user_page: Page) -> Pages:
    return Pages(old_user_page)


# ============================================================
# Class Scope - Old User Authenticated
# ============================================================


@pytest.fixture(scope="class")
def class_old_user_context(
    browser: Browser, old_user: dict
) -> Generator[BrowserContext, None, None]:
    ctx = create_auth_context(browser, old_user)
    yield ctx
    ctx.close()


@pytest.fixture(scope="class")
def class_old_user_page(
    class_old_user_context: BrowserContext,
) -> Generator[Page, None, None]:
    pg = class_old_user_context.new_page()
    yield pg
    pg.close()


@pytest.fixture(scope="class")
def class_old_user_pages(class_old_user_page: Page) -> Pages:
    return Pages(class_old_user_page)


# ============================================================
# Function Scope - Guest (no auth)
# ============================================================


@pytest.fixture
def guest_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    ctx = create_guest_context(browser)
    yield ctx
    ctx.close()


@pytest.fixture
def guest_page(guest_context: BrowserContext) -> Generator[Page, None, None]:
    pg = guest_context.new_page()
    yield pg
    pg.close()


@pytest.fixture
def guest_pages(guest_page: Page) -> Pages:
    return Pages(guest_page)


# ============================================================
# Class Scope - Guest (no auth, shared page within class)
# ============================================================


@pytest.fixture(scope="class")
def class_guest_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    ctx = create_guest_context(browser)
    yield ctx
    ctx.close()


@pytest.fixture(scope="class")
def class_guest_page(class_guest_context: BrowserContext) -> Generator[Page, None, None]:
    pg = class_guest_context.new_page()
    yield pg
    pg.close()


@pytest.fixture(scope="class")
def class_guest_pages(class_guest_page: Page) -> Pages:
    return Pages(class_guest_page)


# ============================================================
# Hooks
# ============================================================


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = (
            item.funcargs.get("page")
            or item.funcargs.get("guest_page")
            or item.funcargs.get("class_page")
            or item.funcargs.get("class_guest_page")
            or item.funcargs.get("old_user_page")
            or item.funcargs.get("class_old_user_page")
        )
        if page and not page.is_closed():
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.error(f"Test failed: {item.name}")


def pytest_configure(config):
    logger.info(f"Test environment: {settings.ENV}")
    logger.info(f"Base URL: {settings.BASE_URL}")
