import requests
import random
from typing import Optional
from faker import Faker
from models import AuthModel
from actor import Actor
from const import PB_API_COLLECTIONS, SUPERUSER_EMAIL, SUPERUSER_PASSWORD

fake = Faker()


class ActorOrchestrator:
    def __init__(self):
        self.superuser: Optional[AuthModel] = None
        self.users: list[Actor] = []

    def superuser_login(self):
        url = PB_API_COLLECTIONS.format(
            collection="_superusers", operation="auth-with-password"
        )
        data = {"identity": SUPERUSER_EMAIL, "password": SUPERUSER_PASSWORD}
        resp = requests.post(url, json=data)
        resp.raise_for_status()
        auth = resp.json()
        self.superuser = AuthModel(id=auth["record"]["id"], token=auth["token"])
        return self.superuser

    def create_users(self, count=20):
        """
        Generate users and store as Actor instances.
        """
        self.users = []
        for i in range(count):
            full_name = fake.first_name()
            email = f"{full_name.lower()}.{i}@test.com"
            password = "password"

            # create user
            url = PB_API_COLLECTIONS.format(collection="users", operation="records")
            data = {
                "email": email,
                "password": password,
                "passwordConfirm": password,
                "name": full_name,
            }
            resp = requests.post(url, json=data)
            resp.raise_for_status()

            # login user
            url = PB_API_COLLECTIONS.format(
                collection="users", operation="auth-with-password"
            )
            data = {"identity": email, "password": password}
            resp = requests.post(url, json=data)
            resp.raise_for_status()
            auth_data = resp.json()
            auth = AuthModel(id=auth_data["record"]["id"], token=auth_data["token"])

            self.users.append(Actor(auth))

    def act_create_teams(self, chance=0.5):
        """
        Each user has a chance to create a team.
        """
        for user in self.users:
            if random.random() < chance:
                user.create_team()

    def act_join_teams(self):
        for actor in self.users:
            actor.request_to_join_teams()

    def act_join_and_approve(self, max_joins=2, approve_ratio=0.9):
        # first, all users request to join teams
        for actor in self.users:
            actor.request_to_join_teams(max_joins=max_joins)

        # then, all captains approve pending requests
        for actor in self.users:
            actor.approve_pending_members(approve_ratio=approve_ratio)

    def act_submit_game_requests(self):
        for user in self.users:
            user.submit_game_request()
