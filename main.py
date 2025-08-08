import requests
import json
import random
import string
import os
import shutil
import subprocess
import threading
import time
import json
import random
import json
import random
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from faker import Faker

fake = Faker()


@dataclass
class AuthModel:
    id: str
    token: str


PB_API_BASE_URL = "http://127.0.0.1:8090/api/"
PB_API_COLLECTIONS = PB_API_BASE_URL + "collections/{collection}/{operation}"
PB_ROOT = "/home/loucasp/pelada-backend/"
PB_DATA_DIR = PB_ROOT + "pb_data"
PB_EXEC = PB_ROOT + "pelada-backend"
SUPERUSER_EMAIL = "loukis500@gmail.com"
SUPERUSER_PASSWORD = "Banana123!"
WORKER_COUNT = 100
LOG_FILE = "./pb_server.log"


barrier = threading.Barrier(WORKER_COUNT)


def wait_for_server(url, timeout=10):
    print("Waiting for server to start...", end="")
    for _ in range(timeout * 10):
        try:
            resp = requests.get(url)
            if resp.status_code < 500:
                print("done")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    raise Exception("PocketBase server did not start in time.")


def initialize_pocketbase():
    global SUPER_AUTH
    subprocess.run(["pkill", "-f", "pelada-backend"])

    if os.path.exists(PB_DATA_DIR):
        shutil.rmtree(PB_DATA_DIR)

    subprocess.run(["go", "build"], cwd=PB_ROOT)

    subprocess.run(
        [
            "./pelada-backend",
            "superuser",
            "upsert",
            SUPERUSER_EMAIL,
            SUPERUSER_PASSWORD,
        ],
        cwd=PB_ROOT,
    )

    log_file_handler = open(LOG_FILE, "w")

    # Start server
    server_proc = subprocess.Popen(
        ["./pelada-backend", "serve", "--dev"],
        cwd=PB_ROOT,
        stdout=log_file_handler,
        stderr=log_file_handler,
    )

    # Wait for HTTP server to come online
    wait_for_server(PB_API_BASE_URL + "health")

    # Now it's safe to send HTTP requests
    url = PB_API_COLLECTIONS.format(
        collection="_superusers", operation="auth-with-password"
    )
    data = {
        "identity": SUPERUSER_EMAIL,
        "password": SUPERUSER_PASSWORD,
    }
    resp = requests.post(url, json=data)
    auth = resp.json()

    SUPER_AUTH = AuthModel(id=auth["record"]["id"], token=auth["token"])

    return server_proc, log_file_handler


def create_user_and_login(thread_id) -> AuthModel:
    full_name = fake.first_name()  # e.g., "John Smith"
    # Convert name to email-safe format
    email_name = full_name.lower().replace(" ", ".").replace("'", "")
    email = f"{email_name}.{thread_id}@test.com"
    password = "password"

    url = PB_API_COLLECTIONS.format(collection="users", operation="records")
    data = {
        "email": email,
        "password": password,
        "passwordConfirm": password,
        "name": full_name,
    }
    resp = requests.post(url, json=data)

    url = PB_API_COLLECTIONS.format(collection="users", operation="auth-with-password")
    data = {
        "identity": email,
        "password": password,
    }
    resp = requests.post(url, json=data)

    d = json.loads(resp.content)
    return AuthModel(id=d["record"]["id"], token=d["token"])


def create_team(auth: AuthModel):
    url = PB_API_COLLECTIONS.format(collection="teams", operation="records")
    data = {
        "teamName": f"{fake.color_name()} {fake.word()}",
        "teamStrength": random.choice(["beginner", "intermediate", "advanced"]),
    }
    headers = {"Authorization": f"Bearer {auth.token}"}
    resp = requests.post(url, json=data, headers=headers)
    return resp


def join_random_team(auth: AuthModel):
    # Get all teams
    url = PB_API_COLLECTIONS.format(collection="teams", operation="records")
    headers = {"Authorization": f"Bearer {auth.token}"}
    resp = requests.get(url, headers=headers)
    teams = json.loads(resp.content)["items"]
    if len(teams) < 1:
        return

    # Pick a random team
    team_id = random.choice(teams)["id"]

    # Create a join request (pending state)
    url = PB_API_COLLECTIONS.format(collection="teamMembers", operation="records")
    data = {
        "team": team_id,
        "user": auth.id,
        "state": "pending",  # request to join
    }
    headers = {
        "Authorization": f"Bearer {SUPER_AUTH.token}"
    }  # superuser to bypass normal rules for testing
    resp = requests.post(url, json=data, headers=headers)
    return resp


def approve_pending_members(auth: AuthModel):
    """
    Simulate captain approving pending join requests for their teams.
    """
    # Get teams where I'm a captain
    url = PB_API_COLLECTIONS.format(collection="teamMembers", operation="records")
    headers = {"Authorization": f"Bearer {auth.token}"}
    params = {"filter": f"(user='{auth.id}' && isCaptain=true)"}
    resp = requests.get(url, headers=headers, params=params)
    my_captain_teams = json.loads(resp.content)["items"]

    for entry in my_captain_teams:
        team_id = entry["team"]

        # Get all pending members for that team
        url = PB_API_COLLECTIONS.format(collection="teamMembers", operation="records")
        params = {"filter": f"(team='{team_id}' && state='pending')"}
        resp = requests.get(url, headers=headers, params=params)
        pending_members = json.loads(resp.content)["items"]

        # Approve each one
        for pm in pending_members:
            member_id = pm["id"]
            update_url = PB_API_COLLECTIONS.format(
                collection="teamMembers", operation=f"records/{member_id}"
            )
            data = {"state": "active"}
            requests.patch(update_url, json=data, headers=headers)


def generate_slots_json(n=5):
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


def generate_game_request(auth: AuthModel, team: str):
    url = PB_API_COLLECTIONS.format(collection="venues", operation="records")
    headers = {"Authorization": f"Bearer {auth.token}"}
    params = {"perPage": 100}
    resp = requests.get(url, params=params, headers=headers)
    venue_id = json.loads(resp.content)["items"][0]["id"]
    time_slots = generate_slots_json(random.randint(1, 4))

    url = PB_API_COLLECTIONS.format(collection="gameRequests", operation="records")
    data = {"venue": venue_id, "timeSlots": time_slots, "team": team}
    resp = requests.post(url, params=params, headers=headers, json=data)


def submit_game_request(auth: AuthModel):
    # if not a captain, return
    # get teams, check if im the captain]
    url = PB_API_COLLECTIONS.format(collection="teamMembers", operation="records")
    headers = {"Authorization": f"Bearer {auth.token}"}
    params = {"filter": f"(user='{auth.id}')"}
    resp = requests.get(url, headers=headers, params=params)
    my_teams = json.loads(resp.content)["items"]
    for team_member_entry in my_teams:
        if bool(team_member_entry["isCaptain"]):
            generate_game_request(auth, team_member_entry["team"])


def worker_func(thread_id):
    auth = create_user_and_login(thread_id)
    if random.random() > 0.5:
        create_team(auth)
    else:
        join_random_team(auth)

    try:
        barrier.wait()
    except threading.BrokenBarrierError:
        print(f"Barrier broken for thread {thread_id}")

    # If captain, approve pending join requests
    approve_pending_members(auth)

    # If captain of a team, submit game request
    submit_game_request(auth)

    try:
        barrier.wait()
    except threading.BrokenBarrierError:
        print(f"Barrier broken for thread {thread_id}")

    if thread_id == 1:
        call_game_matcher_cron()


def call_game_matcher_cron():
    url = PB_API_BASE_URL + "crons/game-matcher"
    headers = {"Authorization": f"Bearer {SUPER_AUTH.token}"}
    requests.post(url, headers=headers)


def populate_db():
    print("Populating databse...", end="")
    threads = []

    for i in range(WORKER_COUNT):
        thread = threading.Thread(target=worker_func, args=(i + 1,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("done")


if __name__ == "__main__":
    server_handler = None
    log_file_handler = None

    try:
        server_handler, log_file_handler = initialize_pocketbase()
        populate_db()
        print("Server is ready")
        server_handler.wait()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Shutting down...")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        subprocess.run(["pkill", "-f", "pelada-backend"])
        raise  # <-- re-raise so the full traceback is visible
    finally:
        if server_handler:
            server_handler.terminate()
            try:
                server_handler.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_handler.kill()
        if log_file_handler:
            log_file_handler.close()
