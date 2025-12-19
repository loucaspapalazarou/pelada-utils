from pathlib import Path
import platform


# ----- PocketBase configuration -----
PB_PORT = "8091"
PB_API_BASE_URL = f"http://127.0.0.1:{PB_PORT}/api/"
PB_API_COLLECTIONS = PB_API_BASE_URL + "collections/{collection}/{operation}"

# Determine PB_ROOT depending on OS
if platform.system() == "Windows":
    PB_ROOT = Path("D:/MY_FILES/Projects/pelada-backend")
else:
    PB_ROOT = Path("/home/loucasp/pelada-backend")

PB_DATA_DIR = PB_ROOT / "pb_data"

# # Executable name
# PB_EXEC = PB_ROOT / (
#     "pelada-backend.exe" if platform.system() == "Windows" else "pelada-backend"
# )

# Admin credentials
SUPERUSER_EMAIL = "loukis500@gmail.com"
SUPERUSER_PASSWORD = "password"

# Server settings
WORKER_COUNT = 100
LOG_FILE = Path("./pb_server.log")
