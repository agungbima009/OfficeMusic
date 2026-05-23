from pathlib import Path

# Root project directory (2 levels up dari file ini: app/core/ -> app/ -> root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

MAX_RESULTS = 10

# Path absolut lintas platform (Windows & Linux)
DOWNLOAD_FOLDER = BASE_DIR / "music_cache"

VIDEO_FOLDER = BASE_DIR / "video_cache"

DB_PATH = BASE_DIR / "office_music.db"