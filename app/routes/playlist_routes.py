
import os

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from urllib.parse import unquote

from app.services.playlist_service import (
    get_playlist,
    delete_song,
    get_song_detail,
    get_all_playlists,
    get_songs_in_playlist,
    add_song_to_playlist,
    remove_song_from_playlist,
    delete_playlist,
    create_playlist,
    get_playlist_stream_urls
)

router = APIRouter()

DOWNLOAD_FOLDER = "music_cache"


# =========================================
# MODELS
# =========================================
class PlaylistAddRequest(BaseModel):
    playlist_name: str
    song_filename: str


class PlaylistCreateRequest(BaseModel):
    playlist_name: str


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
@router.get("/stream/{filename:path}")
async def stream_music(filename: str):

    filename = unquote(filename)

    file_path = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    if not os.path.exists(file_path):

        return {
            "status": False,
            "message": "Music not found"
        }

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename
    )


# =========================================
# DELETE MUSIC
# =========================================
@router.delete("/playlist/{filename}")
def delete_music(filename: str):

    result = delete_song(filename)

    return result


# =========================================
# MUSIC DETAIL
# =========================================
@router.get("/playlist/detail/{filename}")
def detail_music(filename: str):

    result = get_song_detail(filename)

    return result


# =========================================
# GET ALL PLAYLISTS
# =========================================
@router.get("/playlists")
def list_playlists():

    playlists = get_all_playlists()

    return {
        "status": True,
        "playlists": playlists
    }


# =========================================
# CREATE PLAYLIST
# =========================================
@router.post("/playlists/create")
def create_new_playlist(data: PlaylistCreateRequest):

    result = create_playlist(
        data.playlist_name
    )

    return result


# =========================================
# PLAYLIST STREAM URLS
# =========================================
@router.get("/playlists/{playlist_name}/stream")
def stream_playlist(playlist_name: str):

    urls = get_playlist_stream_urls(
        playlist_name
    )

    return {
        "status": True,
        "playlist_name": playlist_name,
        "stream_urls": urls
    }


# =========================================
# ADD SONG TO PLAYLIST
# =========================================
@router.post("/playlists")
def add_to_playlist(data: PlaylistAddRequest):

    result = add_song_to_playlist(
        data.playlist_name,
        data.song_filename
    )

    return result


# =========================================
# PLAYLIST DETAIL
# =========================================
@router.get("/playlists/{playlist_name}")
def playlist_detail(playlist_name: str):

    songs = get_songs_in_playlist(
        playlist_name
    )

    return {
        "status": True,
        "playlist_name": playlist_name,
        "total": len(songs),
        "songs": songs
    }


# =========================================
# DELETE PLAYLIST
# =========================================
@router.delete("/playlists/{playlist_name}")
def remove_playlist(playlist_name: str):

    result = delete_playlist(
        playlist_name
    )

    return result


# =========================================
# REMOVE SONG FROM PLAYLIST
# =========================================
@router.delete("/playlists/{playlist_name}/{filename}")
def remove_from_playlist(
    playlist_name: str,
    filename: str
):

    result = remove_song_from_playlist(
        playlist_name,
        filename
    )

    return result
