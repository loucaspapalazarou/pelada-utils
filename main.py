import time
import argparse

from server import PocketBaseServer
from orchestrator import ActorOrchestrator


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
            
            orchestrator = ActorOrchestrator()
            orchestrator.populate()

            if args.mode == "populate":
                print("Population complete. Shutting down.")
                return

            print("\033[92mServer ready\033[0m")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("KeyboardInterrupt received. Shutting down...")


if __name__ == "__main__":
    main()
