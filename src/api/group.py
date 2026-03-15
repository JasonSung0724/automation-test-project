from api.base import BaseAPI
from config.settings import settings


class GroupAPI(BaseAPI):
    def __init__(self, token: str = None):
        token = token or settings.AUTH_TOKEN
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        super().__init__(headers)

    def get_groups(self) -> list:
        return self.get("/groups").json()

    def get_personal_ledger(self) -> dict:
        return self.get("/groups/personal-ledger").json()

    def create_group(
        self, name: str, currency: str = "TWD", member_names: list[str] | None = None
    ) -> dict:
        payload = {"name": name, "currency": currency}
        if member_names:
            payload["member_names"] = member_names
        return self.post("/groups", json=payload).json()

    def get_group(self, group_id: str) -> dict:
        return self.get(f"/groups/{group_id}").json()

    def update_group(self, group_id: str, payload: dict) -> dict:
        return self.put(f"/groups/{group_id}", json=payload).json()

    def delete_group(self, group_id: str) -> None:
        self.delete(f"/groups/{group_id}")

    def join_group(self, group_id: str, member_id: str) -> dict:
        return self.post(f"/groups/{group_id}/join", json={"member_id": member_id}).json()

    def add_member(self, group_id: str, display_name: str) -> dict:
        return self.post(
            f"/groups/{group_id}/members", json={"display_name": display_name}
        ).json()

    def create_transaction(self, group_id: str, payload: dict) -> dict:
        return self.post(f"/transactions/group/{group_id}", json=payload).json()
