import requests

from config.settings import settings
from core.logger import logger

_shared_session = requests.Session()


class BaseAPI:
    def __init__(self, headers: dict = None):
        self.base_url = settings.API_BASE_URL
        self.headers = headers or {}
        self.timeout = 15
        self.session = _shared_session

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        timeout = kwargs.pop("timeout", self.timeout)

        logger.info(f"{method.upper()} {url}")
        resp = self.session.request(
            method,
            url,
            headers=self.headers,
            timeout=timeout,
            **kwargs,
        )

        if resp.status_code >= 400:
            logger.error(f"Response {resp.status_code}: {resp.text}")

        resp.raise_for_status()
        return resp

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)
