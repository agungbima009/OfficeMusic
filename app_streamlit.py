import os
from math import ceil
from typing import Dict, List
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv

# ======================================================
# LOAD ENV
# ======================================================
load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    ""
).rstrip("/")

if not BACKEND_URL:
    st.error("BACKEND_URL belum diset")
    st.stop()

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="OfficeMusic",
    page_icon="🎵",
    layout="wide"
)

# ======================================================
# SESSION
# ======================================================
@st.cache_resource
def get_session():

    session = requests.Session()

    adapter = requests.adapters.HTTPAdapter(
        pool_connections=20,
        pool_maxsize=20,
        max_retries=2
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


session = get_session()

# ======================================================
# CACHE API
# ======================================================
@st.cache_data(ttl=60)
def get_songs() -> List[Dict]:

    try:

        r = session.get(
            f"{BACKEND_URL}/playlist",
            timeout=10
        )

        if r.status_code == 200:
            return r.json().get("songs", [])

    except Exception:
        pass

    return []


@st.cache_data(ttl=60)
def get_playlists():

    try:

        r = session.get(
            f"{BACKEND_URL}/playlists",
            timeout=10
        )

        if r.status_code == 200:
            return r.json().get("playlists", [])

    except Exception:
        pass

    return []


@st.cache_data(ttl=60)
def get_playlist_detail(name):

    try:

        r = session.get(
            f"{BACKEND_URL}/playlists/{quote(name)}",
            timeout=10
        )

        if r.status_code == 200:
            return r.json().get("songs", [])

    except Exception:
        pass

    return []


def clear_cache():
    st.cache_data.clear()

# ======================================================
# PLAYER SESSION STATE
# ======================================================
if "current_audio" not in st.session_state:
    st.session_state.current_audio = None

if "current_song_name" not in st.session_state:
    st.session_state.current_song_name = None

if "playlist_queue" not in st.session_state:
    st.session_state.playlist_queue = []

if "playlist_queue_names" not in st.session_state:
    st.session_state.playlist_queue_names = []

if "playlist_index" not in st.session_state:
    st.session_state.playlist_index = 0

# ======================================================
# CSS
# ======================================================
st.markdown("""
<style>

.block-container{
    padding-top:2rem;
}

.main-title{
    text-align:center;
    font-size:3rem;
    font-weight:800;
}

.sub-title{
    text-align:center;
    color:#9CA3AF;
    margin-bottom:2rem;
}

.music-card{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:18px;
    padding:15px;
    margin-bottom:20px;
}

.music-title{
    font-weight:700;
    margin-top:10px;
    min-height:55px;
}

.music-channel{
    color:#9CA3AF;
    font-size:0.8rem;
    margin-bottom:10px;
}

.stButton button{
    width:100%;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================
st.markdown(
    "<div class='main-title'>🎵 OfficeMusic</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='sub-title'>Modern Music Streaming</div>",
    unsafe_allow_html=True
)

# ======================================================
# HEALTH CHECK
# ======================================================
try:

    health = session.get(
        BACKEND_URL,
        timeout=5
    )

    if health.status_code != 200:
        st.error("Backend Offline")
        st.stop()

except Exception as e:

    st.error(f"Backend Error: {e}")
    st.stop()

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.title("📂 Menu")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🎵 Library",
        "📁 Playlist"
    ]
)

if st.sidebar.button("♻️ Refresh Cache"):

    clear_cache()

    st.toast("Cache refreshed")

# ======================================================
# SIDEBAR PLAYER
# ======================================================
with st.sidebar:

    st.markdown("---")

    st.markdown("## 🎧 Player")

    if st.session_state.current_audio:

        st.write(
            f"**{st.session_state.current_song_name}**"
        )

        st.audio(
            st.session_state.current_audio,
            format="audio/mp3"
        )

    else:

        st.info("Belum ada musik diputar")

# ======================================================
# LIBRARY
# ======================================================
if menu == "🎵 Library":

    st.title("🎵 Library")

    songs = get_songs()

    if not songs:

        st.info("Library kosong")

    else:

        search = st.text_input(
            "Cari lagu"
        ).lower()

        filtered = []

        for song in songs:

            title = song.get(
                "title",
                ""
            ).lower()

            if search in title:

                filtered.append(song)

        PAGE_SIZE = 12

        total_pages = ceil(
            len(filtered) / PAGE_SIZE
        )

        page = st.number_input(
            "Page",
            min_value=1,
            max_value=max(total_pages, 1),
            value=1
        )

        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE

        page_songs = filtered[start:end]

        cols = st.columns(4)

        for idx, song in enumerate(page_songs):

            with cols[idx % 4]:

                st.markdown(
                    "<div class='music-card'>",
                    unsafe_allow_html=True
                )

                if song.get("thumbnail"):

                    st.image(
                        song["thumbnail"],
                        use_container_width=True
                    )

                st.markdown(
                    f"<div class='music-title'>{song['title']}</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div class='music-channel'>{song.get('channel', 'Local')}</div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "▶️ Play",
                    key=f"play_{idx}"
                ):

                    audio_url = (
                        f"{BACKEND_URL}"
                        f"/player/stream/"
                        f"{quote(song['filename'])}"
                    )

                    st.session_state.current_audio = (
                        audio_url
                    )

                    st.session_state.current_song_name = (
                        song["title"]
                    )

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

# ======================================================
# PLAYLIST
# ======================================================
elif menu == "📁 Playlist":

    st.title("📁 Playlist")

    playlists = get_playlists()

    if not playlists:

        st.info("Belum ada playlist")

    else:

        selected_playlist = st.selectbox(
            "Pilih Playlist",
            playlists
        )

        songs = get_playlist_detail(
            selected_playlist
        )

        st.write(f"Total Lagu: {len(songs)}")

        if st.button("▶️ Putar Semua"):

            queue = []
            queue_names = []

            for song in songs:

                queue.append(
                    f"{BACKEND_URL}"
                    f"/player/stream/"
                    f"{quote(song['filename'])}"
                )

                queue_names.append(
                    song["title"]
                )

            st.session_state.playlist_queue = queue

            st.session_state.playlist_queue_names = (
                queue_names
            )

            st.session_state.playlist_index = 0

            if queue:

                st.session_state.current_audio = (
                    queue[0]
                )

                st.session_state.current_song_name = (
                    queue_names[0]
                )

            st.rerun()

        if st.session_state.playlist_queue:

            prev_col, next_col = st.columns(2)

            with prev_col:

                if st.button("⏮️ Prev"):

                    st.session_state.playlist_index = max(
                        0,
                        st.session_state.playlist_index - 1
                    )

                    idx = st.session_state.playlist_index

                    st.session_state.current_audio = (
                        st.session_state.playlist_queue[idx]
                    )

                    st.session_state.current_song_name = (
                        st.session_state.playlist_queue_names[idx]
                    )

                    st.rerun()

            with next_col:

                if st.button("⏭️ Next"):

                    st.session_state.playlist_index = min(
                        len(st.session_state.playlist_queue) - 1,
                        st.session_state.playlist_index + 1
                    )

                    idx = st.session_state.playlist_index

                    st.session_state.current_audio = (
                        st.session_state.playlist_queue[idx]
                    )

                    st.session_state.current_song_name = (
                        st.session_state.playlist_queue_names[idx]
                    )

                    st.rerun()

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")

st.caption("OfficeMusic Debian 13 VPS Optimized")