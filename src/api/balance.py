from api.base import BaseAPI


class BalanceAPI(BaseAPI):
    def __init__(self, token: str):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        super().__init__(headers)

    def get_balance(self, group_id: str) -> dict:
        return self.get(f"/groups/{group_id}/balance").json()

    def get_stats(self, group_id: str) -> dict:
        return self.get(f"/groups/{group_id}/stats").json()
