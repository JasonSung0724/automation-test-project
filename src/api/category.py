from api.base import BaseAPI


class CategoryAPI(BaseAPI):
    def __init__(self, token: str):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        super().__init__(headers)

    def get_categories(self, group_id: str) -> list:
        return self.get(f"/categories/{group_id}").json()

    def get_preset_categories(self, category_type: str = "expense") -> list:
        return self.get("/categories/presets", params={"category_type": category_type}).json()
