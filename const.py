from pathlib import Path


# ----- PocketBase configuration -----
PB_IP = "127.0.0.1"
PB_PORT = "8091"
PB_API_BASE_URL = f"http://{PB_IP}:{PB_PORT}/api/"
PB_API_COLLECTIONS = PB_API_BASE_URL + "collections/{collection}/{operation}"

# PB_ROOT relative to this file (assumes pelada-backend is sibling folder)
PB_ROOT = Path(__file__).parent.parent / "pelada-backend"
PB_DATA_DIR = PB_ROOT / "pb_data"

# Admin credentials
SUPERUSER_EMAIL = "loukis500@gmail.com"
SUPERUSER_PASSWORD = "password"

# Server settings
LOG_FILE = Path(__file__).parent / "pb_server.log"
