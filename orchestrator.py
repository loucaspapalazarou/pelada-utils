import requests
import random
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from faker import Faker
from tqdm import tqdm
from models import AuthModel
from actor import Actor
from const import (
    PB_API_COLLECTIONS,
    SUPERUSER_EMAIL,
    SUPERUSER_PASSWORD,
    PB_API_BASE_URL,
)

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

    def call_game_matcher_cron(self):
        if self.superuser is None:
            raise ValueError(
                "Superuser must be logged in first. Call superuser_login()."
            )
        url = PB_API_BASE_URL + "crons/game-matcher"
        headers = {"Authorization": f"Bearer {self.superuser.token}"}
        requests.post(url, headers=headers)

    def create_users(self, count=20, max_workers=10):
        """
        Generate users and store as Actor instances using multiple threads.
        """
        self.users = []

        def create_single_user(i):
            full_name = fake.first_name()
            email = f"{full_name.lower()}{i}@test.com"
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

            return Actor(auth)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(create_single_user, i): i for i in range(count)}
            for future in tqdm(as_completed(futures), total=count, desc="Creating users"):
                self.users.append(future.result())

    def _run_parallel(self, func, items, desc, max_workers=10):
        """Helper to run a function on items in parallel with progress bar."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(func, item) for item in items]
            for _ in tqdm(as_completed(futures), total=len(futures), desc=desc):
                pass

    def act_create_teams(self, chance=0.5, max_workers=10):
        """
        Each user has a chance to create a team.
        """
        def maybe_create_team(user):
            if random.random() < chance:
                user.create_team()

        self._run_parallel(maybe_create_team, self.users, "Creating teams", max_workers)

    def act_join_teams(self, max_workers=10):
        self._run_parallel(
            lambda actor: actor.request_to_join_teams(),
            self.users,
            "Joining teams",
            max_workers,
        )

    def act_join_and_approve(self, max_joins=2, approve_ratio=0.9, max_workers=10):
        # first, all users request to join teams
        self._run_parallel(
            lambda actor: actor.request_to_join_teams(max_joins=max_joins),
            self.users,
            "Requesting to join teams",
            max_workers,
        )

        # then, all captains approve pending requests
        self._run_parallel(
            lambda actor: actor.approve_pending_members(approve_ratio=approve_ratio),
            self.users,
            "Approving members",
            max_workers,
        )

    def act_submit_game_requests(self, max_workers=10):
        self._run_parallel(
            lambda user: user.submit_game_request(),
            self.users,
            "Submitting game requests",
            max_workers,
        )

    def act_accept_matched_game_requests(self, max_workers=10):
        """
        All actors attempt to accept game requests
        for teams they captain.
        """
        self._run_parallel(
            lambda actor: actor.accept_matched_game_requests(),
            self.users,
            "Accepting game requests",
            max_workers,
        )

    def act_interact_with_messages(self, max_workers=10):
        self._run_parallel(
            lambda actor: actor.send_messages(),
            self.users,
            "Sending messages",
            max_workers,
        )

        self._run_parallel(
            lambda actor: actor.edit_own_messages(),
            self.users,
            "Editing messages",
            max_workers,
        )

        # for actor in self.users:
        #     actor.delete_own_messages()
