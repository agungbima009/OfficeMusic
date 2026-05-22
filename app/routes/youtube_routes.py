from fastapi import APIRouter

from app.models.youtube_model import (
    SearchRequest
)

from app.services.youtube_service import (
    youtube_search_music
)

from app.services.download_service import (
    download_audio,
    download_video
)

router = APIRouter()

# =========================================
# SEARCH MUSIC
# =========================================
@router.post("/search")
def search_music(data: SearchRequest):

    results = youtube_search_music(
        data.query
    )

    return {
        "status": True,
        "results": results
    }

# =========================================
# DOWNLOAD AUDIO
# =========================================
@router.post("/download-audio")
def download_music(video: dict):

    file_path, cached = download_audio(
        video
    )

    return {

        "status": True,

        "cached": cached,

        "file_path": file_path
    }

# =========================================
# DOWNLOAD VIDEO
# =========================================
@router.post("/download-video")
def download_movie(video: dict):

    file_path, cached = download_video(
        video
    )

    return {

        "status": True,

        "cached": cached,

        "file_path": file_path
    }