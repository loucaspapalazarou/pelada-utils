from datetime import datetime, timedelta, timezone
import random
import json
from models import AuthModel
from const import *
import requests


def _generate_slots_json(n=5):
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


def login_as(email, password="password") -> AuthModel:
    url = PB_API_COLLECTIONS.format(collection="users", operation="auth-with-password")
    data = {"identity": email, "password": password}
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    auth_data = resp.json()
    return AuthModel(id=auth_data["record"]["id"], token=auth_data["token"])


def get_teams(auth: AuthModel, isCaptain=None) -> list[str]:
    headers = {"Authorization": f"Bearer {auth.token}"}
    # Fetch teams where this actor is captain
    url = PB_API_COLLECTIONS.format(collection="teams", operation="records")
    if isCaptain is None:
        params = {}
    else:
        params = (
            {"filter": f"(captain='{auth.id}')"}
            if isCaptain
            else {"filter": f"(captain!='{auth.id}')"}
        )
    resp = requests.get(url, headers=headers, params=params)
    teams = resp.json().get("items", [])
    return [team["id"] for team in teams]


def submit_game_request(auth: AuthModel, team_id: str):
    headers = {"Authorization": f"Bearer {auth.token}"}

    # Get a venue
    url = PB_API_COLLECTIONS.format(collection="venues", operation="records")
    resp = requests.get(url, headers=headers, params={"perPage": 100})
    venues = resp.json().get("items", [])
    if not venues:
        return
    venue_id = random.choice(venues)["id"]

    time_slots = _generate_slots_json(random.randint(1, 4))

    url = PB_API_COLLECTIONS.format(collection="gameRequests", operation="records")
    data = {"team": team_id, "venue": venue_id, "timeSlots": time_slots}
    resp = requests.post(url, headers=headers, json=data)


def get_messages(auth):
    headers = {"Authorization": f"Bearer {auth.token}"}
    # Fetch teams where this actor is captain
    url = PB_API_COLLECTIONS.format(collection="messages", operation="records")
    resp = requests.get(url, headers=headers)
    msgs = resp.json().get("items", [])
    return msgs


auth = login_as("tracy.19@test.com")
print("me:", auth.id)
msgs = get_messages(auth)

print(len(msgs))

# for msg in msgs:
#     print(json.dumps(msg, indent=2))


# isCaptain = True
# auth = login_as("ariel.19@test.com")
# print("me:", auth.id)
# cap_team = get_teams(auth, isCaptain=isCaptain)[0]
# print("my team", cap_team)
# submit_game_request(auth, cap_team)
