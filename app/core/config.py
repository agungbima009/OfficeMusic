from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("YOUR_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL")

if not API_KEY:
    raise ValueError("YouTube API KEY not found")

if not BACKEND_URL:
    raise ValueError("Backend URL not found")