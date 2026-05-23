import os
from math import ceil
from typing import Dict, List
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit.components.v1 import html

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
# SESSION POOL
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

        return []

    except Exception:
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

        return []

    except Exception:
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

        return []

    except Exception:
        return []


def clear_cache():
    st.cache_data.clear()

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
    margin-bottom:0;
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
    transition:0.2s;
    height:100%;
}

.music-card:hover{
    transform:translateY(-4px);
    border-color:#7C3AED;
}

.music-title{
    font-weight:700;
    margin-top:10px;
    line-height:1.3;
    font-size:0.95rem;
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
    "<div class='sub-title'>Modern Local Music Streaming</div>",
    unsafe_allow_html=True
)

# ======================================================
# HEALTH CHECK
# ======================================================
try:

    health = session.get(
        BACKEND_URL,
        timeout=3
    )

    if health.status_code != 200:
        st.error("Backend Offline")
        st.stop()

except Exception:
    st.error("Backend Offline")
    st.stop()

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.title("📂 Menu")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🔍 Cari Musik",
        "🎵 Library",
        "📁 Playlist"
    ]
)

if st.sidebar.button("♻️ Refresh Cache"):

    clear_cache()

    st.toast("Cache Refreshed")

# ======================================================
# PLAYER STATE
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
# SIDEBAR PLAYER
# ======================================================
with st.sidebar:

    st.markdown("---")

    st.markdown("## 🎧 Player")

    if st.session_state.current_audio:

        current_name = (
            st.session_state.current_song_name
            or "Unknown Music"
        )

        audio_url = st.session_state.current_audio

        unique_audio_url = (
            f"{audio_url}?v="
            f"{st.session_state.playlist_index}"
        )

        st.write(f"**{current_name}**")

        st.audio(
            unique_audio_url,
            format="audio/mp3"
        )

    else:

        st.info("Belum ada musik diputar")

# ======================================================
# SEARCH MUSIC
# ======================================================
if menu == "🔍 Cari Musik":

    st.title("🔍 Cari Musik")

    query = st.text_input(
        "Cari Lagu",
        placeholder="Coldplay - Yellow"
    )

    if query:

        with st.spinner("Searching..."):

            r = session.post(
                f"{BACKEND_URL}/youtube/search",
                json={"query": query},
                timeout=30
            )

        if r.status_code == 200:

            results = r.json().get("results", [])

            cols = st.columns(4)

            for idx, item in enumerate(results):

                with cols[idx % 4]:

                    st.markdown(
                        "<div class='music-card'>",
                        unsafe_allow_html=True
                    )

                    st.image(
                        item["thumbnail"],
                        use_container_width=True
                    )

                    st.markdown(
                        f"<div class='music-title'>{item['title']}</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"<div class='music-channel'>{item['channel']}</div>",
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "📥 Download",
                        key=f"download_{idx}"
                    ):

                        with st.spinner("Downloading..."):

                            dl = session.post(
                                f"{BACKEND_URL}/youtube/download-audio",
                                json=item,
                                timeout=120
                            )

                        if dl.status_code == 200:

                            clear_cache()

                            st.success("Downloaded")

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

# ======================================================
# LIBRARY
# ======================================================
elif menu == "🎵 Library":

    st.title("🎵 Library")

    songs = get_songs()

    if not songs:

        st.info("Library kosong")

    else:

        search = st.text_input(
            "Filter Lagu",
            placeholder="Cari lagu..."
        ).lower()

        filtered = []

        for song in songs:

            if search in song.get(
                "title",
                ""
            ).lower():

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

        playlists = get_playlists()

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

                else:
                    st.markdown("# 🎵")

                st.markdown(
                    f"<div class='music-title'>{song['title']}</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div class='music-channel'>{song.get('channel', 'Local')}</div>",
                    unsafe_allow_html=True
                )

                # PLAY
                if st.button(
                    "▶️ Play",
                    key=f"play_{idx}"
                ):

                    stream_url = (
                        f"{BACKEND_URL}"
                        f"/player/stream/"
                        f"{quote(song['filename'])}"
                    )

                    st.session_state.current_audio = (
                        stream_url
                    )

                    st.session_state.current_song_name = (
                        song["title"]
                    )

                    st.rerun()

                # ADD TO PLAYLIST
                if playlists:

                    selected_playlist = st.selectbox(
                        "Playlist",
                        ["-"] + playlists,
                        key=f"playlist_select_{idx}"
                    )

                    if selected_playlist != "-":

                        if st.button(
                            "➕ Add",
                            key=f"add_{idx}"
                        ):

                            add = session.post(
                                f"{BACKEND_URL}/playlists",
                                json={
                                    "playlist_name": selected_playlist,
                                    "song_filename": song["filename"]
                                }
                            )

                            if add.status_code == 200:

                                clear_cache()

                                st.success("Added")

                # DELETE
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{idx}"
                ):

                    delete = session.delete(
                        f"{BACKEND_URL}/playlist/{quote(song['filename'])}"
                    )

                    if delete.status_code == 200:

                        clear_cache()

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

    st.subheader("➕ Create Playlist")

    new_playlist = st.text_input(
        "Nama Playlist"
    )

    if st.button("Create Playlist"):

        if new_playlist:

            create = session.post(
                f"{BACKEND_URL}/playlists/create",
                json={
                    "playlist_name": new_playlist
                }
            )

            if create.status_code == 200:

                clear_cache()

                st.rerun()

    st.markdown("---")

    if playlists:

        selected_playlist = st.selectbox(
            "Pilih Playlist",
            playlists
        )

        songs = get_playlist_detail(
            selected_playlist
        )

        st.write(f"Total Lagu: {len(songs)}")

        # PLAY ALL
        if st.button("▶️ Putar Semua Lagu"):

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

        # NEXT PREV
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

        st.markdown("---")

        cols = st.columns(4)

        for idx, song in enumerate(songs):

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
                    f"<div class='music-channel'>{song.get('channel', '')}</div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "▶️ Play",
                    key=f"playlist_play_{idx}"
                ):

                    stream_url = (
                        f"{BACKEND_URL}"
                        f"/player/stream/"
                        f"{quote(song['filename'])}"
                    )

                    st.session_state.current_audio = (
                        stream_url
                    )

                    st.session_state.current_song_name = (
                        song["title"]
                    )

                    st.rerun()

                if st.button(
                    "❌ Remove",
                    key=f"remove_{idx}"
                ):

                    remove = session.delete(
                        f"{BACKEND_URL}/playlists/{selected_playlist}/{quote(song['filename'])}"
                    )

                    if remove.status_code == 200:

                        clear_cache()

                        st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

        st.markdown("---")

        if st.button("🗑️ Delete Playlist"):

            delete = session.delete(
                f"{BACKEND_URL}/playlists/{selected_playlist}"
            )

            if delete.status_code == 200:

                clear_cache()

                st.rerun()

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")

st.caption("Optimized OfficeMusic For Debian 13 VPS")