import time
import sys
import argparse

from server import PocketBaseServer
from orchestrator import ActorOrchestrator


def populate_db():
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["run", "populate"],
        default="run",
        help="run = start server and keep running, populate = seed DB and exit",
    )
    args = parser.parse_args()

    with PocketBaseServer() as server:
        try:
            server.start()

            if args.mode == "populate":
                populate_db()
                print("Population complete. Shutting down.")
                return

            populate_db()
            print("Server ready")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("KeyboardInterrupt received. Shutting down...")


if __name__ == "__main__":
    main()
