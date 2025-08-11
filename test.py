from main import AuthModel, PB_API_COLLECTIONS
import requests
import json

auth = AuthModel(
    id="uwj52q51v2zxhik",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb2xsZWN0aW9uSWQiOiJfcGJfdXNlcnNfYXV0aF8iLCJleHAiOjE3NTU1MzgxMDksImlkIjoidXdqNTJxNTF2Mnp4aGlrIiwicmVmcmVzaGFibGUiOnRydWUsInR5cGUiOiJhdXRoIn0.b6dgxuZ54sHk3VyZKkFvtxonwfhPMjX3baDwtWL9inI",
)


def send_message(auth: AuthModel):
    # Get all teams where user is active (not just captain)
    url = PB_API_COLLECTIONS.format(collection="teamMembers", operation="records")
    headers = {"Authorization": f"Bearer {auth.token}"}
    params = {"filter": f"(user='{auth.id}'&&state='active')", "perPage": 1000}
    resp = requests.get(url, headers=headers, params=params)
    team_memberships = resp.json().get("items", [])

    if not team_memberships:
        return

    # For each team, get accepted game requests
    for tm in team_memberships:
        url = PB_API_COLLECTIONS.format(collection="games", operation="records")
        resp = requests.get(url, headers=headers)
        print(resp.content)
        games = resp.json().get("items", [])

        for game_req in games:
            # Prepare message data
            message_text = "test message 3"  # random sentence as message
            message_data = {
                "user": auth.id,
                "game": game_req["id"],
                "text": message_text,
            }
            url = PB_API_COLLECTIONS.format(collection="messages", operation="records")
            resp = requests.post(url, headers=headers, json=message_data)
            print(resp.content)


send_message(auth)
