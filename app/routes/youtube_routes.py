from fastapi import APIRouter, HTTPException
from urllib.parse import unquote

from app.models.youtube_model import (
    SearchRequest
)

from app.services.youtube_service import (
    youtube_search_music
)

from app.services.download_service import (
    download_audio,
    download_video,
    DOWNLOAD_STATUS
)

router = APIRouter()

# =========================================
# SEARCH MUSIC
# =========================================
@router.post("/search")
def search_music(data: SearchRequest):
    try:
        results = youtube_search_music(
            data.query
        )
        return {
            "status": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal melakukan pencarian musik YouTube: {str(e)}"
        )

# =========================================
# DOWNLOAD AUDIO
# =========================================
@router.post("/download-audio")
def download_music(video: dict):
    try:
        file_path, cached = download_audio(
            video
        )
        return {
            "status": True,
            "cached": cached,
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mendownload audio dari YouTube: {str(e)}"
        )

# =========================================
# DOWNLOAD VIDEO
# =========================================
@router.post("/download-video")
def download_movie(video: dict):
    try:
        file_path, cached = download_video(
            video
        )
        return {
            "status": True,
            "cached": cached,
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mendownload video dari YouTube: {str(e)}"
        )

# =========================================
# DOWNLOAD STATUS (POLLING)
# =========================================
@router.get("/download-status")
def get_download_status(url: str):
    """
    Cek progress download satu URL — O(1) dict lookup.
    Query param: ?url=<youtube_url>
    """
    decoded_url = unquote(url)
    status = DOWNLOAD_STATUS.get(decoded_url)
    if status is None:
        return {"status": "not_started", "percentage": 0.0}
    return status