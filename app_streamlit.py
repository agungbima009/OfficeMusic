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

    if st.session_state.playlist_queue:
        import json

        queue_json = json.dumps(st.session_state.playlist_queue)
        names_json = json.dumps(st.session_state.playlist_queue_names)
        current_idx = st.session_state.playlist_index

        player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                    color: #F3F4F6;
                    overflow: hidden;
                }}
                
                .player-card {{
                    background: linear-gradient(135deg, rgba(31, 41, 55, 0.7), rgba(17, 24, 39, 0.9));
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 20px;
                    padding: 20px;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
                    backdrop-filter: blur(12px);
                    max-width: 100%;
                    box-sizing: border-box;
                }}

                .now-playing-label {{
                    font-size: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.15em;
                    color: #A78BFA;
                    font-weight: 700;
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }}

                .pulse-dot {{
                    width: 6px;
                    height: 6px;
                    background-color: #A78BFA;
                    border-radius: 50%;
                    animation: pulse 1.5s infinite alternate;
                }}

                @keyframes pulse {{
                    0% {{ transform: scale(0.8); opacity: 0.5; }}
                    100% {{ transform: scale(1.3); opacity: 1; }}
                }}

                .track-info {{
                    margin-bottom: 16px;
                    overflow: hidden;
                    position: relative;
                }}

                .track-title {{
                    font-size: 1.05rem;
                    font-weight: 700;
                    margin-bottom: 4px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }}

                .track-queue {{
                    font-size: 0.75rem;
                    color: #9CA3AF;
                    font-weight: 500;
                }}

                .visualizer {{
                    display: flex;
                    align-items: flex-end;
                    justify-content: center;
                    gap: 3px;
                    height: 35px;
                    margin: 15px 0;
                }}

                .bar {{
                    width: 4px;
                    height: 5px;
                    background: linear-gradient(to top, #7C3AED, #A78BFA);
                    border-radius: 2px;
                    transition: height 0.2s ease;
                }}

                .bar.active {{
                    animation: bounce 1s ease-in-out infinite alternate;
                }}

                @keyframes bounce {{
                    0% {{ height: 5px; }}
                    100% {{ height: 35px; }}
                }}

                .bar:nth-child(1) {{ animation-delay: 0.1s; }}
                .bar:nth-child(2) {{ animation-delay: 0.3s; }}
                .bar:nth-child(3) {{ animation-delay: 0.5s; }}
                .bar:nth-child(4) {{ animation-delay: 0.2s; }}
                .bar:nth-child(5) {{ animation-delay: 0.4s; }}
                .bar:nth-child(6) {{ animation-delay: 0.6s; }}
                .bar:nth-child(7) {{ animation-delay: 0.15s; }}
                .bar:nth-child(8) {{ animation-delay: 0.35s; }}

                .progress-container {{
                    margin-bottom: 20px;
                }}

                .time-slider {{
                    -webkit-appearance: none;
                    width: 100%;
                    height: 5px;
                    border-radius: 3px;
                    background: rgba(255, 255, 255, 0.15);
                    outline: none;
                    cursor: pointer;
                    margin-bottom: 8px;
                    transition: background 0.2s;
                }}

                .time-slider:hover {{
                    background: rgba(255, 255, 255, 0.25);
                }}

                .time-slider::-webkit-slider-thumb {{
                    -webkit-appearance: none;
                    appearance: none;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #A78BFA;
                    cursor: pointer;
                    transition: transform 0.1s;
                }}

                .time-slider::-webkit-slider-thumb:hover {{
                    transform: scale(1.3);
                }}

                .time-display {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.75rem;
                    color: #9CA3AF;
                    font-weight: 500;
                }}

                .controls {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 20px;
                }}

                .control-btn {{
                    background: none;
                    border: none;
                    color: #D1D5DB;
                    font-size: 1.25rem;
                    cursor: pointer;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 38px;
                    height: 38px;
                    border-radius: 50%;
                }}

                .control-btn:hover {{
                    color: #FFF;
                    background: rgba(255, 255, 255, 0.08);
                    transform: scale(1.05);
                }}

                .control-btn:active {{
                    transform: scale(0.95);
                }}

                .play-btn {{
                    font-size: 1.5rem;
                    background: linear-gradient(135deg, #7C3AED, #6D28D9);
                    color: #FFF;
                    width: 50px;
                    height: 50px;
                    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
                }}

                .play-btn:hover {{
                    background: linear-gradient(135deg, #8B5CF6, #7C3AED);
                    color: #FFF;
                    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.4);
                }}
            </style>
        </head>
        <body>
            <div class="player-card">
                <div class="now-playing-label">
                    <div class="pulse-dot"></div>
                    <span id="playing-status">Now Playing</span>
                </div>
                
                <div class="track-info">
                    <div class="track-title" id="track-title">Loading track...</div>
                    <div class="track-queue" id="track-queue">Song 0 of 0</div>
                </div>

                <div class="visualizer" id="visualizer">
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                </div>

                <div class="progress-container">
                    <input type="range" class="time-slider" id="time-slider" min="0" max="100" value="0">
                    <div class="time-display">
                        <span id="current-time">0:00</span>
                        <span id="duration">0:00</span>
                    </div>
                </div>

                <div class="controls">
                    <button class="control-btn" id="prev-btn" title="Previous">⏮️</button>
                    <button class="control-btn play-btn" id="play-btn" title="Play/Pause">▶️</button>
                    <button class="control-btn" id="next-btn" title="Next">⏭️</button>
                </div>
            </div>

            <script>
                const pyQueue = {queue_json};
                const pyNames = {names_json};
                const pyIndex = {current_idx};

                let queue = pyQueue;
                let names = pyNames;
                let index = pyIndex;
                let isResuming = false;

                // Sync with localStorage to handle Streamlit reruns
                const localQueueStr = localStorage.getItem("office_music_queue");
                if (localQueueStr) {{
                    try {{
                        const localQueue = JSON.parse(localQueueStr);
                        if (JSON.stringify(localQueue) === JSON.stringify(pyQueue)) {{
                            const localIndex = localStorage.getItem("office_music_index");
                            if (localIndex !== null) {{
                                const parsedIndex = parseInt(localIndex, 10);
                                if (parsedIndex >= 0 && parsedIndex < queue.length) {{
                                    index = parsedIndex;
                                    isResuming = true;
                                }}
                            }}
                        }}
                    }} catch(e) {{
                        console.error("Local storage parse error:", e);
                    }}
                }}

                // Save to localStorage
                localStorage.setItem("office_music_queue", JSON.stringify(queue));
                localStorage.setItem("office_music_names", JSON.stringify(names));
                localStorage.setItem("office_music_index", index);

                // Audio Object
                const audio = new Audio();
                audio.src = queue[index];
                audio.preload = "auto";

                // DOM Elements
                const trackTitle = document.getElementById("track-title");
                const trackQueue = document.getElementById("track-queue");
                const playBtn = document.getElementById("play-btn");
                const prevBtn = document.getElementById("prev-btn");
                const nextBtn = document.getElementById("next-btn");
                const timeSlider = document.getElementById("time-slider");
                const currentTimeSpan = document.getElementById("current-time");
                const durationSpan = document.getElementById("duration");
                const visualizerBars = document.querySelectorAll(".bar");
                const playingStatus = document.getElementById("playing-status");

                function formatTime(secs) {{
                    if (isNaN(secs)) return "0:00";
                    const m = Math.floor(secs / 60);
                    const s = Math.floor(secs % 60).toString().padStart(2, '0');
                    return `${{m}}:${{s}}`;
                }}

                function updateTrackUI() {{
                    trackTitle.textContent = names[index];
                    trackQueue.textContent = `Song ${{index + 1}} of ${{queue.length}}`;
                }}

                function toggleVisualizer(isPlaying) {{
                    visualizerBars.forEach(bar => {{
                        if (isPlaying) {{
                            bar.classList.add("active");
                        }} else {{
                            bar.classList.remove("active");
                        }}
                    }});
                }}

                function playSong(idx) {{
                    index = idx;
                    audio.src = queue[index];
                    localStorage.setItem("office_music_index", index);
                    localStorage.setItem("office_music_time", "0");
                    updateTrackUI();
                    
                    audio.play()
                        .then(() => {{
                            playBtn.textContent = "⏸️";
                            playingStatus.textContent = "Now Playing";
                            toggleVisualizer(true);
                        }})
                        .catch(err => {{
                            console.log("Play failed:", err);
                            playBtn.textContent = "▶️";
                            playingStatus.textContent = "Paused";
                            toggleVisualizer(false);
                        }});
                }}

                function playNext() {{
                    if (index + 1 < queue.length) {{
                        playSong(index + 1);
                    }} else {{
                        // Wrap around to start of queue
                        playSong(0);
                    }}
                }}

                function playPrev() {{
                    if (index - 1 >= 0) {{
                        playSong(index - 1);
                    }} else {{
                        // Wrap around to end of queue
                        playSong(queue.length - 1);
                    }}
                }}

                // Listeners
                playBtn.addEventListener('click', () => {{
                    if (audio.paused) {{
                        audio.play()
                            .then(() => {{
                                playBtn.textContent = "⏸️";
                                playingStatus.textContent = "Now Playing";
                                toggleVisualizer(true);
                            }})
                            .catch(err => console.log(err));
                    }} else {{
                        audio.pause();
                        playBtn.textContent = "▶️";
                        playingStatus.textContent = "Paused";
                        toggleVisualizer(false);
                    }}
                }});

                prevBtn.addEventListener('click', playPrev);
                nextBtn.addEventListener('click', playNext);

                audio.addEventListener('timeupdate', () => {{
                    if (!isNaN(audio.duration)) {{
                        const progress = (audio.currentTime / audio.duration) * 100;
                        timeSlider.value = progress;
                        currentTimeSpan.textContent = formatTime(audio.currentTime);
                        durationSpan.textContent = formatTime(audio.duration);
                        
                        // Save play time
                        localStorage.setItem("office_music_time", audio.currentTime);
                        localStorage.setItem("office_music_index", index);
                    }}
                }});

                timeSlider.addEventListener('input', () => {{
                    if (!isNaN(audio.duration)) {{
                        const newTime = (timeSlider.value / 100) * audio.duration;
                        audio.currentTime = newTime;
                    }}
                }});

                audio.addEventListener('ended', playNext);

                audio.addEventListener('loadedmetadata', () => {{
                    durationSpan.textContent = formatTime(audio.duration);
                }});

                // Initialize
                updateTrackUI();

                if (isResuming) {{
                    const savedTime = localStorage.getItem("office_music_time");
                    if (savedTime) {{
                        audio.currentTime = parseFloat(savedTime);
                    }}
                    audio.play()
                        .then(() => {{
                            playBtn.textContent = "⏸️";
                            playingStatus.textContent = "Now Playing";
                            toggleVisualizer(true);
                        }})
                        .catch(err => {{
                            console.log("Autoplay resume blocked:", err);
                            playBtn.textContent = "▶️";
                            playingStatus.textContent = "Paused";
                            toggleVisualizer(false);
                        }});
                }} else {{
                    // Brand new play, trigger autoplay
                    audio.play()
                        .then(() => {{
                            playBtn.textContent = "⏸️";
                            playingStatus.textContent = "Now Playing";
                            toggleVisualizer(true);
                        }})
                        .catch(err => {{
                            console.log("Autoplay blocked:", err);
                            playBtn.textContent = "▶️";
                            playingStatus.textContent = "Paused";
                            toggleVisualizer(false);
                        }});
                }}
            </script>
        </body>
        </html>
        """

        html(player_html, height=270)

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

                    st.session_state.playlist_queue = [stream_url]
                    st.session_state.playlist_queue_names = [song["title"]]
                    st.session_state.playlist_index = 0

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

                    st.session_state.playlist_queue = [stream_url]
                    st.session_state.playlist_queue_names = [song["title"]]
                    st.session_state.playlist_index = 0

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