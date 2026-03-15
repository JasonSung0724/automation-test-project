from enum import StrEnum
from typing import Any

from config.settings import settings


class Locale(StrEnum):
    EN = "en"
    ZH_TW = "zh-TW"
    JA = "ja"
    TH = "th"


TRANSLATIONS: dict[str, dict[str, str]] = {
    "groups.personal_ledger": {
        "en": "{name}'s Personal Ledger",
        "zh-TW": "{name}的個人帳本",
        "zh-CN": "{name}的个人账本",
        "ja": "{name}の個人台帳",
    },
    "groups.create_group": {
        "en": "Create Group",
        "zh-TW": "建立群組",
        "zh-CN": "创建群组",
        "ja": "グループを作成",
    },
    "groups.no_groups": {
        "en": "No groups yet",
        "zh-TW": "尚無群組",
        "zh-CN": "暂无群组",
        "ja": "グループがありません",
    },
    "auth.logout": {
        "en": "Logout",
        "zh-TW": "登出",
        "zh-CN": "退出",
        "ja": "ログアウト",
    },
    "common.submit": {
        "en": "Submit",
        "zh-TW": "送出",
        "zh-CN": "提交",
        "ja": "送信",
    },
    "common.cancel": {
        "en": "Cancel",
        "zh-TW": "取消",
        "zh-CN": "取消",
        "ja": "キャンセル",
    },
    "common.save": {
        "en": "Save",
        "zh-TW": "儲存",
        "zh-CN": "保存",
        "ja": "保存",
    },
    "common.delete": {
        "en": "Delete",
        "zh-TW": "刪除",
        "zh-CN": "删除",
        "ja": "削除",
    },
    "common.confirm": {
        "en": "Confirm",
        "zh-TW": "確認",
        "zh-CN": "确认",
        "ja": "確認",
    },
    "common.search": {
        "en": "Search",
        "zh-TW": "搜尋",
        "zh-CN": "搜索",
        "ja": "検索",
    },
    "transaction.expense": {
        "en": "Expense",
        "zh-TW": "支出",
        "zh-CN": "支出",
        "ja": "支出",
    },
    "transaction.income": {
        "en": "Income",
        "zh-TW": "收入",
        "zh-CN": "收入",
        "ja": "収入",
    },
    "transaction.transfer": {
        "en": "Transfer",
        "zh-TW": "轉帳",
        "zh-CN": "转账",
        "ja": "振替",
    },
    "groups.created": {
        "en": "Group created",
        "zh-TW": "已建立群組",
        "zh-CN": "已创建群组",
        "ja": "グループを作成しました",
    },
    "groups.deleted": {
        "en": "Group deleted",
        "zh-TW": "已刪除群組",
        "zh-CN": "已删除群组",
        "ja": "グループを削除しました",
    },
    "profile.updated": {
        "en": "Profile updated",
        "zh-TW": "已更新個人資料",
        "zh-CN": "已更新个人资料",
        "ja": "プロフィールを更新しました",
    },
}


class I18n:
    def __init__(self, locale: str = None):
        self.locale = locale or settings.LOCALE

    def t(self, key: str, **kwargs: Any) -> str:
        if key not in TRANSLATIONS:
            raise KeyError(f"Translation key not found: {key}")

        translations = TRANSLATIONS[key]

        if self.locale not in translations:
            text = translations.get("en", key)
        else:
            text = translations[self.locale]

        if kwargs:
            text = text.format(**kwargs)

        return text

    def __call__(self, key: str, **kwargs: Any) -> str:
        return self.t(key, **kwargs)


i18n = I18n()
