from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.playlist_service import (
    get_playlist,
    delete_song,
    get_song_detail,
    get_all_playlists,
    get_songs_in_playlist,
    add_song_to_playlist,
    remove_song_from_playlist,
    delete_playlist
)

from app.core.constants import (
    DOWNLOAD_FOLDER
)

import os

router = APIRouter()

# =========================================
# MODELS
# =========================================
class PlaylistAddRequest(BaseModel):
    playlist_name: str
    song_filename: str

# =========================================
# GET PLAYLIST
# =========================================
@router.get("/playlist")
def playlist():

    songs = get_playlist()

    return {

        "status": True,

        "total": len(songs),

        "songs": songs
    }

# =========================================
# STREAM AUDIO
# =========================================
@router.get("/stream/{filename}")
def stream_music(filename: str):

    file_path = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    return FileResponse(
        file_path,
        media_type="audio/mpeg"
    )

# =========================================
# DELETE MUSIC
# =========================================
@router.delete("/playlist/{filename}")
def delete_music(filename: str):

    result = delete_song(
        filename
    )

    return result

# =========================================
# MUSIC DETAIL
# =========================================
@router.get("/playlist/detail/{filename}")
def detail_music(filename: str):

    result = get_song_detail(
        filename
    )

    return result


# =========================================
# PLAYLIST GROUPS (DB Driven)
# =========================================

@router.get("/playlists")
def list_playlists():
    playlists = get_all_playlists()
    return {
        "status": True,
        "playlists": playlists
    }

@router.post("/playlists")
def add_to_playlist(data: PlaylistAddRequest):
    result = add_song_to_playlist(
        data.playlist_name,
        data.song_filename
    )
    return result

@router.get("/playlists/{playlist_name}")
def playlist_detail(playlist_name: str):
    songs = get_songs_in_playlist(playlist_name)
    return {
        "status": True,
        "playlist_name": playlist_name,
        "total": len(songs),
        "songs": songs
    }

@router.delete("/playlists/{playlist_name}")
def remove_playlist(playlist_name: str):
    result = delete_playlist(playlist_name)
    return result

@router.delete("/playlists/{playlist_name}/{filename}")
def remove_from_playlist(playlist_name: str, filename: str):
    result = remove_song_from_playlist(
        playlist_name,
        filename
    )
    return result