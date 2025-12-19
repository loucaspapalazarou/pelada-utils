import time

from server import PocketBaseServer
from orchestrator import ActorOrchestrator

if __name__ == "__main__":
    with PocketBaseServer() as server:
        try:
            server.start()

            orchestrator = ActorOrchestrator()
            orchestrator.superuser_login()

            if orchestrator.superuser is not None:
                print(f"Superuser logged in: {orchestrator.superuser.id}")
            else:
                print("Failed to log in superuser")

            orchestrator.create_users(count=20)
            orchestrator.act_create_teams(chance=0.5)
            orchestrator.act_join_teams()
            orchestrator.act_join_and_approve()
            # orchestrator.act_submit_game_requests() -> broken (maybe its the actual code)

            print("Server ready")

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("KeyboardInterrupt received. Shutting down...")
