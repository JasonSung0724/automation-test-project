from api.base import BaseAPI


class TransactionAPI(BaseAPI):
    def __init__(self, token: str):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        super().__init__(headers)

    def get_transactions(self, group_id: str, limit: int = 30, offset: int = 0) -> dict:
        return self.get(
            f"/transactions/group/{group_id}",
            params={"limit": limit, "offset": offset},
        ).json()

    def create_transaction(self, group_id: str, payload: dict) -> dict:
        return self.post(f"/transactions/group/{group_id}", json=payload).json()

    def get_transaction(self, transaction_id: str) -> dict:
        return self.get(f"/transactions/{transaction_id}").json()

    def update_transaction(self, transaction_id: str, payload: dict) -> dict:
        return self.put(f"/transactions/{transaction_id}", json=payload).json()

    def delete_transaction(self, transaction_id: str) -> None:
        self.delete(f"/transactions/{transaction_id}")
