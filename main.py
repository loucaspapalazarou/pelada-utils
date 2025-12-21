import time
import sys

from server import PocketBaseServer
from orchestrator import ActorOrchestrator

if __name__ == "__main__":
    with PocketBaseServer() as server:
        try:
            server.start()

            print("Populating database")
            sys.stdout.flush()

            orchestrator = ActorOrchestrator()
            orchestrator.superuser_login()
            orchestrator.create_users(count=50)
            orchestrator.act_create_teams(chance=0.5)
            orchestrator.act_join_teams()
            orchestrator.act_join_and_approve()
            orchestrator.act_submit_game_requests()
            orchestrator.call_game_matcher_cron()
            orchestrator.act_accept_matched_game_requests()
            orchestrator.act_interact_with_messages()

            print("Server ready")

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("KeyboardInterrupt received. Shutting down...")
