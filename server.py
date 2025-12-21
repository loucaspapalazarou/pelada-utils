import requests
import platform
import time
import subprocess
import os
import shutil
from const import *


class PocketBaseServer:
    def __init__(
        self, pb_root=PB_ROOT, pb_port=PB_PORT, pb_ip=PB_IP, log_file=LOG_FILE
    ):
        self.pb_root = pb_root
        self.pb_ip = pb_ip
        self.pb_port = pb_port
        self.log_file_path = log_file
        self.process = None
        self.log_handler = None

    def start(self, kill_existing=True, remove_data=True):
        if kill_existing:
            self.kill_existing_server()

        if remove_data and os.path.exists(PB_DATA_DIR):
            shutil.rmtree(PB_DATA_DIR)
            print("Removed old data")

        # Ensure superuser exists
        subprocess.run(
            [
                "go",
                "run",
                "main.go",
                "superuser",
                "upsert",
                SUPERUSER_EMAIL,
                SUPERUSER_PASSWORD,
            ],
            cwd=self.pb_root,
            check=True,
        )

        # Open log file
        self.log_handler = open(self.log_file_path, "w")

        # Start server
        self.process = subprocess.Popen(
            [
                "go",
                "run",
                "main.go",
                "serve",
                "--dev",
                f"--http={self.pb_ip}:{self.pb_port}",
            ],
            cwd=self.pb_root,
            stdout=self.log_handler,
            stderr=self.log_handler,
        )

        self.wait_for_server(PB_API_BASE_URL + "health")

    def wait_for_server(self, url, timeout=10):
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

    def kill_existing_server(self):
        system = platform.system()
        if system == "Windows":
            cmd = ["taskkill", "/F", "/IM", "pelada-backend.exe"]
        else:
            cmd = ["pkill", "-f", "pelada-backend"]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Killed existing server")

    def terminate(self, timeout=5, force=True):
        """Terminate the PocketBase server, optionally force kill if it hangs."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=timeout)
                print("PocketBase server terminated")
            except subprocess.TimeoutExpired:
                if force:
                    print("Terminate timed out, force killing server...")
                    self.process.kill()
                    self.process.wait()
                    print("PocketBase server force killed")
        if self.log_handler:
            self.log_handler.close()
            self.log_handler = None

    def __enter__(self):
        """Enable use as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()
