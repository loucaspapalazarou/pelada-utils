import requests
import random
import json
from const import PB_API_COLLECTIONS
from models import AuthModel
import json
import random
from datetime import datetime, timedelta, timezone
from const import PB_API_COLLECTIONS
from faker import Faker


class Actor:
    def __init__(self, auth: AuthModel):
        self.auth = auth

    def create_team(self):
        url = PB_API_COLLECTIONS.format(collection="teams", operation="records")
        data = {
            "teamName": f"Team {random.randint(1000,9999)}",
            "teamStrength": random.choice(["beginner", "intermediate", "advanced"]),
        }
        headers = {"Authorization": f"Bearer {self.auth.token}"}
        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        team = resp.json()
        return team

    def request_to_join_teams(self, max_joins=2):
        """Submit join requests to random teams."""
        url = PB_API_COLLECTIONS.format(collection="teams", operation="records")
        headers = {"Authorization": f"Bearer {self.auth.token}"}
        resp = requests.get(url, headers=headers)
        teams = resp.json().get("items", [])

        if not teams:
            return []

        random.shuffle(teams)
        teams_to_join = teams[:max_joins]

        results = []
        for team in teams_to_join:
            join_url = PB_API_COLLECTIONS.format(
                collection="teamMembers", operation="records"
            )
            data = {"team": team["id"], "user": self.auth.id, "state": "pending"}
            resp = requests.post(join_url, json=data, headers=headers)
            results.append(resp)
        return results

    def approve_pending_members(self, approve_ratio=0.9):
        """Approve pending join requests for all teams where this user is the captain."""
        headers = {"Authorization": f"Bearer {self.auth.token}"}

        # Fetch teams where user is captain
        url = PB_API_COLLECTIONS.format(collection="teams", operation="records")
        params = {"filter": f"(captain='{self.auth.id}')"}
        resp = requests.get(url, headers=headers, params=params)
        captain_teams = resp.json().get("items", [])

        for team in captain_teams:
            team_id = team["id"]

            # Fetch pending members for this team
            url = PB_API_COLLECTIONS.format(
                collection="teamMembers", operation="records"
            )
            params = {"filter": f"(team='{team_id}'&&state='pending')"}
            resp = requests.get(url, headers=headers, params=params)
            pending_members = resp.json().get("items", [])

            for member in pending_members:
                state = "active" if random.random() < approve_ratio else "rejected"
                update_url = PB_API_COLLECTIONS.format(
                    collection="teamMembers", operation=f"records/{member['id']}"
                )
                data = {"state": state, "user": member["user"], "team": team_id}
                requests.patch(update_url, json=data, headers=headers)

    def submit_game_request(self):
        """Each captain submits one game request per team."""
        headers = {"Authorization": f"Bearer {self.auth.token}"}
        # Fetch teams where this actor is captain
        url = PB_API_COLLECTIONS.format(collection="teams", operation="records")
        params = {"filter": f"(captain='{self.auth.id}')"}
        resp = requests.get(url, headers=headers, params=params)
        captain_teams = resp.json().get("items", [])

        for team in captain_teams:
            team_id = team["id"]

            # Get a venue
            url = PB_API_COLLECTIONS.format(collection="venues", operation="records")
            resp = requests.get(url, headers=headers, params={"perPage": 100})
            venues = resp.json().get("items", [])
            if not venues:
                continue
            venue_id = random.choice(venues)["id"]

            # Generate 1-4 random time slots
            time_slots = self._generate_slots_json(random.randint(1, 4))

            # Create game request
            url = PB_API_COLLECTIONS.format(
                collection="gameRequests", operation="records"
            )
            data = {"team": team_id, "venue": venue_id, "timeSlots": time_slots}
            requests.post(url, headers=headers, json=data)

    def _generate_slots_json(self, n=5):
        def round_to_next_half_hour(dt):
            if dt.minute < 30:
                return dt.replace(minute=30, second=0, microsecond=0)
            else:
                dt = dt.replace(minute=0, second=0, microsecond=0)
                return dt + timedelta(hours=1)

        slots = []
        now = datetime.now(timezone.utc)
        for _ in range(n):
            random_minutes = random.randint(1, 7 * 24 * 60)
            start = round_to_next_half_hour(now + timedelta(minutes=random_minutes))
            end = start + timedelta(hours=1)
            slots.append(
                {
                    "start": start.isoformat().replace("+00:00", "Z"),
                    "end": end.isoformat().replace("+00:00", "Z"),
                }
            )
        return json.dumps(slots, indent=2)
