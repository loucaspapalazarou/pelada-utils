from pathlib import Path
import subprocess
import os

# ----- Repository configuration -----
BACKEND_REPO_URL = "https://github.com/loucaspapalazarou/pelada-backend.git"
COMMON_REPO_URL = "https://github.com/loucaspapalazarou/pelada-common.git"

# Local paths (repos will be cloned here)
REPOS_DIR = Path(__file__).parent / "repos"
BACKEND_DIR = REPOS_DIR / "pelada-backend"
COMMON_DIR = REPOS_DIR / "pelada-common"

# ----- PocketBase configuration -----
PB_IP = "0.0.0.0"
PB_PORT = "8091"
PB_API_BASE_URL = f"http://{PB_IP}:{PB_PORT}/api/"
PB_API_COLLECTIONS = PB_API_BASE_URL + "collections/{collection}/{operation}"

# PB_ROOT points to the cloned backend
PB_ROOT = BACKEND_DIR
PB_DATA_DIR = BACKEND_DIR / "pb_data"

# Admin credentials
SUPERUSER_EMAIL = "loukis500@gmail.com"
SUPERUSER_PASSWORD = "password"

# Server settings
LOG_FILE = Path(__file__).parent / "pb_server.log"


def clone_or_pull_repo(repo_url: str, target_dir: Path, branch: str = "main") -> None:
    """Clone a repo if it doesn't exist, or pull latest changes if it does."""
    if target_dir.exists():
        print(f"Pulling latest changes for {target_dir.name}...")
        subprocess.run(
            ["git", "pull", "origin", branch],
            cwd=target_dir,
            check=True,
            capture_output=True,
        )
    else:
        print(f"Cloning {repo_url}...")
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            check=True,
            capture_output=True,
        )


def setup_repos() -> None:
    """Ensure both backend and common repos are cloned and up to date."""
    clone_or_pull_repo(BACKEND_REPO_URL, BACKEND_DIR)
    clone_or_pull_repo(COMMON_REPO_URL, COMMON_DIR)

    # Generate constants from common schema
    print("Generating constants from schema...")
    subprocess.run(
        ["python", "generator/generate.py"],
        cwd=COMMON_DIR,
        check=True,
        capture_output=True,
    )
    print("Repos ready.")
