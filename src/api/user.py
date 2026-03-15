from api.base import BaseAPI
from config.settings import settings


class UserAPI(BaseAPI):
    def __init__(self, token: str = None):
        if token:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            headers = {"Content-Type": "application/json"}
        super().__init__(headers)

    def _test_key_headers(self) -> dict:
        return {
            "X-Test-Key": settings.TEST_KEY,
            "Content-Type": "application/json",
        }

    def create_test_user(self, display_name: str = "E2E Bot") -> dict:
        original_headers = self.headers
        self.headers = self._test_key_headers()
        try:
            return self.post(
                "/auth/test/create-user",
                json={"display_name": display_name},
            ).json()
        finally:
            self.headers = original_headers

    def delete_test_user(self, user_id: str) -> dict:
        original_headers = self.headers
        self.headers = self._test_key_headers()
        try:
            return self.delete(
                "/auth/test/delete-user",
                json={"user_id": user_id},
            ).json()
        finally:
            self.headers = original_headers

    def get_me(self) -> dict:
        return self.get("/users/me").json()
