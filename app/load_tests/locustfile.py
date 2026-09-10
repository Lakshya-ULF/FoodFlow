from locust import HttpUser, task


ENDPOINT = "/api/v1/benchmark/restaurants/db"


class FoodFlowUser(HttpUser):

    @task
    def restaurants(self):
        self.client.get(
            f"{ENDPOINT}?limit=10&offset=0"
        )