import requests
import json
import random
import string
import os
import shutil
import subprocess
import threading
import time
import sys
from dataclasses import dataclass

PB_API_BASE_URL = "http://127.0.0.1:8090/api/"
PB_API_COLLECTIONS = PB_API_BASE_URL + "collections/{collection}/{operation}"
PB_ROOT = "/home/loucasp/pelada-backend/"
PB_DATA_DIR = PB_ROOT + "pb_data"
PB_EXEC = PB_ROOT + "pelada-backend"
SUPERUSER_EMAIL = "loukis500@gmail.com"
SUPERUSER_PASSWORD = "Banana123!"
WORKER_COUNT = 100
LOG_FILE = "./pb_server.log"


@dataclass
class AuthModel:
    id: str
    token: str


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
    url = PB_API_BASE_URL.format(
        collection="_superusers", operation="auth-with-password"
    )
    data = {
        "identity": SUPERUSER_EMAIL,
        "password": SUPERUSER_PASSWORD,
    }
    resp = requests.post(url, json=data)
    auth = resp.json()

    # super_user = AuthModel(id=auth["record"]["id"], token=auth["token"])

    return server_proc, log_file_handler


def create_user_and_login(thread_id) -> tuple[str, str]:
    email = f"user{thread_id}@test.com"
    password = "password"

    url = PB_API_COLLECTIONS.format(collection="users", operation="records")
    data = {
        "email": email,
        "password": password,
        "passwordConfirm": password,
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
        "teamName": "team_name",
        "teamStrength": "beginner",
        "captainId": auth.id,
    }
    headers = {"Authorization": f"Bearer {auth.token}"}
    resp = requests.post(url, json=data, headers=headers)
    return resp


def worker_func(thread_id):
    auth_model = create_user_and_login(thread_id)
    create_team(auth_model)


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
    try:
        server_handler, log_file_handler = initialize_pocketbase()
        populate_db()
        print("Server is ready")
        server_handler.wait()
    except KeyboardInterrupt:
        print("Exiting...", end="")
        server_handler.terminate()
        server_handler.wait()
        log_file_handler.close()
        print("bye")
        sys.exit()
