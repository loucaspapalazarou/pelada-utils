from pathlib import Path
from dotenv import load_dotenv
import subprocess
import os

# Load environment variables
load_dotenv()

# ----- Repository configuration -----
BACKEND_REPO_URL = "https://github.com/loucaspapalazarou/pelada-backend.git"
COMMON_REPO_URL = "https://github.com/loucaspapalazarou/pelada-common.git"

# Local paths from env or fallback to cloning repos
_backend_env = os.getenv("BACKEND_PATH")
_common_env = os.getenv("COMMON_PATH")

# Repos directory for cloned repos (fallback)
REPOS_DIR = Path(__file__).parent / "repos"

# Resolve paths - use env if set, otherwise clone to repos dir
if _backend_env:
    BACKEND_DIR = Path(_backend_env).resolve()
    USE_LOCAL_BACKEND = True
else:
    BACKEND_DIR = REPOS_DIR / "pelada-backend"
    USE_LOCAL_BACKEND = False

if _common_env:
    COMMON_DIR = Path(_common_env).resolve()
    USE_LOCAL_COMMON = True
else:
    COMMON_DIR = REPOS_DIR / "pelada-common"
    USE_LOCAL_COMMON = False

# ----- PocketBase configuration -----
PB_IP = os.getenv("PB_IP", "0.0.0.0")
PB_PORT = os.getenv("PB_PORT", "8091")
PB_API_BASE_URL = f"http://{PB_IP}:{PB_PORT}/api/"
PB_API_COLLECTIONS = PB_API_BASE_URL + "collections/{collection}/{operation}"

# PB_ROOT points to the backend directory
PB_ROOT = BACKEND_DIR
PB_DATA_DIR = BACKEND_DIR / "pb_data"

# Admin credentials
SUPERUSER_EMAIL = os.getenv("SUPERUSER_EMAIL", "test@example.com")
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD", "testpassword123")

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
    """Ensure both backend and common repos are available."""
    # Only clone if not using local paths
    if not USE_LOCAL_BACKEND:
        clone_or_pull_repo(BACKEND_REPO_URL, BACKEND_DIR)
    else:
        print(f"Using local backend: {BACKEND_DIR}")
        if not BACKEND_DIR.exists():
            raise FileNotFoundError(f"BACKEND_PATH does not exist: {BACKEND_DIR}")

    if not USE_LOCAL_COMMON:
        clone_or_pull_repo(COMMON_REPO_URL, COMMON_DIR)
    else:
        print(f"Using local common: {COMMON_DIR}")
        if not COMMON_DIR.exists():
            raise FileNotFoundError(f"COMMON_PATH does not exist: {COMMON_DIR}")

    # Generate constants from common schema (only if not using local - local should already be generated)
    if not USE_LOCAL_COMMON:
        print("Generating constants from schema...")
        subprocess.run(
            ["python", "generator/generate.py"],
            cwd=COMMON_DIR,
            check=True,
            capture_output=True,
        )
    
    print("Repos ready.")
