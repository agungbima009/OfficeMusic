from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("YOUR_API_KEY")

if not API_KEY:
    raise ValueError("YouTube API KEY not found")