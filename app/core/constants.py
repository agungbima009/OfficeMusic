import os
from pathlib import Path

# Root project directory (2 levels up dari file ini: app/core/ -> app/ -> root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAX_RESULTS = 10

# Path absolut lintas platform (Windows & Linux)
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "music_cache")

VIDEO_FOLDER = os.path.join(BASE_DIR, "video_cache")

DB_PATH = Path(BASE_DIR) / "office_music.db"