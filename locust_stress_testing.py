import random
import string

from locust import HttpUser, task, between


def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))


class TaskApiUser(HttpUser):
    wait_time = between(1, 3)  # пауза между запросами в секундах

    @task(2)
    def create_task(self):
        self.client.post("/tasks/", json={
            "title": random_string(12),
            "description": random_string(30),
            "status": "в ожидании",
            "priority": random.randint(1, 5)
        })

    @task(1)
    def list_tasks(self):
        self.client.get("/tasks/")
