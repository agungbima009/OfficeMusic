from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("YOUR_API_KEY")  # Opsional — jika kosong, yt-dlp digunakan sebagai fallback
BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    raise ValueError("Backend URL not found")