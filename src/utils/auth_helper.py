import requests

from config.settings import settings
from core.logger import logger


class AuthHelper:
    @staticmethod
    def get_token() -> str:
        if settings.AUTH_TOKEN:
            logger.debug("Using AUTH_TOKEN from environment")
            return settings.AUTH_TOKEN
        return AuthHelper._fetch_demo_token()

    @staticmethod
    def _fetch_demo_token() -> str:
        url = f"{settings.API_BASE_URL}/auth/demo-token"
        logger.info(f"Fetching demo token from: {url}")
        resp = requests.post(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        token = data.get("token") or data.get("access_token", "")
        logger.debug("Demo token fetched successfully")
        return token

    @staticmethod
    def get_auth_headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
