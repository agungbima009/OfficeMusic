import streamlit as st
import requests
import os
import time
import subprocess

# =========================================
# CONFIG & PAGE CONFIGURATION
# =========================================
st.set_page_config(
    page_title="OfficeMusic - Premium Media Controller",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://localhost:8000"

# =========================================
# AUTO START FASTAPI BACKEND
# =========================================
if "backend_started" not in st.session_state:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RUN_PATH = os.path.join(BASE_DIR, "run.py")

    subprocess.Popen(["python", RUN_PATH])

    st.session_state.backend_started = True
    time.sleep(3)
    
# =========================================
# CUSTOM PREMIUM STYLING (CSS)
# =========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Gradient Title and Header */
    .app-title {
        background: linear-gradient(135deg, #FF2E55 0%, #FF8E53 50%, #5856D6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.2rem;
        text-align: center;
        letter-spacing: -1px;
    }
    .app-subtitle {
        color: #A0AEC0;
        text-align: center;
        font-size: 1.15rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Sidebar Navigation */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #09090E 0%, #121221 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Custom Card Style (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(15px);
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .glass-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 46, 85, 0.3);
        transform: translateY(-4px);
        box-shadow: 0 15px 35px rgba(255, 46, 85, 0.15);
    }
    
    /* Micro-Animations & Custom Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, rgba(88, 86, 214, 0.2) 0%, rgba(255, 46, 85, 0.2) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.25s ease;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #5856D6 0%, #FF2E55 100%);
        border-color: transparent;
        transform: scale(1.03);
        box-shadow: 0 5px 15px rgba(255, 46, 85, 0.4);
    }
    
    /* Streamlit overrides for premium look */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #5856D6 0%, #FF2E55 100%);
    }
    
    /* Song Title styling */
    .song-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.4;
        margin-bottom: 4px;
    }
    
    .song-channel {
        font-size: 0.95rem;
        color: #A0AEC0;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================
# APP HEADER
# =========================================
st.markdown("<div class='app-title'>🎵 OfficeMusic Controller</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Aesthetic Smart Media Server & Local Streaming Client</div>", unsafe_allow_html=True)

# =========================================
# BACKEND HEALTH CHECK
# =========================================
backend_active = False
try:
    health_resp = requests.get(BACKEND_URL, timeout=2)
    if health_resp.status_code == 200 and health_resp.json().get("status"):
        backend_active = True
except Exception:
    backend_active = False

if not backend_active:
    st.error("⚠️ **Server Backend Offline!**")
    st.info("Harap jalankan server backend terlebih dahulu dengan perintah: `python run.py` di terminal Anda agar UI dapat berfungsi.")
    st.stop()

# =========================================
# REAL-TIME PHYSICAL SERVER STATUS (Global Banner)
# =========================================
def show_server_status():
    try:
        current_resp = requests.get(f"{BACKEND_URL}/current")
        if current_resp.status_code == 200:
            current_song = current_resp.json().get("current_song")
            if current_song:
                st.markdown(f"""
                <div class="glass-card" style="background: linear-gradient(135deg, rgba(88, 86, 214, 0.1) 0%, rgba(255, 46, 85, 0.1) 100%); border-color: rgba(255, 46, 85, 0.2); padding: 15px 25px; margin-bottom: 25px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #FF2E55; font-weight: 700;">SERVER FISIK SEDANG MEMUTAR</span>
                            <h3 style="margin: 5px 0 0 0; color: #FFFFFF; font-weight: 600;">🔊 {current_song}</h3>
                        </div>
                        <div style="font-size: 2rem; animation: pulse 2s infinite;">📻</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception:
        pass

show_server_status()

# =========================================
# SIDEBAR NAVIGATION
# =========================================
st.sidebar.markdown("<div style='text-align: center; padding: 10px 0;'><h2 style='color: white; font-weight:700;'>🧭 MENU</h2></div>", unsafe_allow_html=True)
menu = st.sidebar.radio(
    "",
    ["🔍 Cari & Unduh Musik", "🎵 Perpustakaan Lagu", "📂 Playlist Custom", "⚙️ Kontrol Server Fisik"],
    index=1
)

# Sidebar helper details
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="color: #A0AEC0; font-size: 0.85rem; padding: 10px;">
    <strong>ℹ️ Petunjuk:</strong><br>
    • <strong>Stream in Browser:</strong> Putar musik langsung di HP / PC Anda.<br>
    • <strong>Play on Server:</strong> Putar musik secara fisik melalui speaker hardware server.
</div>
""", unsafe_allow_html=True)

# =========================================
# MENU 1: YOUTUBE SEARCH & DOWNLOAD
# =========================================
if menu == "🔍 Cari & Unduh Musik":
    st.markdown("<h2 style='font-weight: 700;'>🔍 YouTube Music Explorer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0AEC0;'>Cari dan unduh lagu dari YouTube langsung ke server. Lagu yang diunduh akan otomatis terintegrasi ke database.</p>", unsafe_allow_html=True)
    
    query = st.text_input("Masukkan judul lagu atau penyanyi:", placeholder="Contoh: Coldplay - Yellow", key="search_query")
    
    if query:
        with st.spinner("Mencari lagu di YouTube..."):
            try:
                search_resp = requests.post(f"{BACKEND_URL}/youtube/search", json={"query": query})
                if search_resp.status_code == 200:
                    results = search_resp.json().get("results", [])
                    if results:
                        st.success(f"Ditemukan {len(results)} musik!")
                        
                        # Display search results as beautiful grid
                        for idx, item in enumerate(results):
                            st.markdown(f"<div class='glass-card'>", unsafe_allow_html=True)
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                st.image(item["thumbnail"], use_column_width=True)
                                
                            with col2:
                                st.markdown(f"<div class='song-title'>{item['title']}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='song-channel'>📺 Channel: {item['channel']}</div>", unsafe_allow_html=True)
                                
                                # Buttons for download
                                btn_col1, btn_col2, btn_col3 = st.columns(3)
                                
                                with btn_col1:
                                    if st.button(f"📥 Unduh MP3", key=f"dl_mp3_{idx}"):
                                        with st.spinner("Mengunduh audio..."):
                                            dl_resp = requests.post(f"{BACKEND_URL}/youtube/download-audio", json=item)
                                            if dl_resp.status_code == 200 and dl_resp.json().get("status"):
                                                info = dl_resp.json()
                                                cached_str = " (Menggunakan Cache)" if info.get("cached") else " (Unduhan Baru)"
                                                st.toast(f"✅ Sukses mengunduh MP3{cached_str}!")
                                                st.success(f"Tersimpan di: `{info.get('file_path')}`")
                                            else:
                                                st.error("Gagal mengunduh audio.")
                                
                                with btn_col2:
                                    if st.button(f"🎥 Unduh MP4", key=f"dl_mp4_{idx}"):
                                        with st.spinner("Mengunduh video..."):
                                            dl_resp = requests.post(f"{BACKEND_URL}/youtube/download-video", json=item)
                                            if dl_resp.status_code == 200 and dl_resp.json().get("status"):
                                                info = dl_resp.json()
                                                cached_str = " (Menggunakan Cache)" if info.get("cached") else " (Unduhan Baru)"
                                                st.toast(f"✅ Sukses mengunduh MP4{cached_str}!")
                                                st.success(f"Tersimpan di: `{info.get('file_path')}`")
                                            else:
                                                st.error("Gagal mengunduh video.")
                                                
                                with btn_col3:
                                    st.markdown(f"<a href='{item['url']}' target='_blank'><button style='width:100%; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:8px 16px; font-weight:600; cursor:pointer;'>🌐 Buka YouTube</button></a>", unsafe_allow_html=True)
                                    
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Musik tidak ditemukan.")
                else:
                    st.error("Gagal melakukan pencarian.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# =========================================
# MENU 2: LOCAL LIBRARY & STREAMING PLAYER
# =========================================
elif menu == "🎵 Perpustakaan Lagu":
    st.markdown("<h2 style='font-weight: 700;'>🎵 Perpustakaan Lagu Lokal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0AEC0;'>Daftar lagu lokal yang terdaftar di database. Anda dapat memutarnya langsung di browser atau melalui speaker server.</p>", unsafe_allow_html=True)
    
    # Reload button
    if st.button("🔄 Refresh Perpustakaan"):
        st.rerun()

    try:
        playlist_resp = requests.get(f"{BACKEND_URL}/playlist")
        if playlist_resp.status_code == 200:
            songs = playlist_resp.json().get("songs", [])
            
            if songs:
                st.write(f"Total Lagu di Library: **{len(songs)}**")
                
                # Render Library Items
                for idx, song in enumerate(songs):
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        # If thumbnail is empty (locally synced), show default icon
                        if song.get("thumbnail"):
                            st.image(song["thumbnail"], use_column_width=True)
                        else:
                            st.markdown("<div style='height: 120px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.03); border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1);'><span style='font-size: 3rem;'>🎵</span></div>", unsafe_allow_html=True)
                            
                    with col2:
                        st.markdown(f"<div class='song-title'>{song['title']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='song-channel'>📺 Source/Channel: {song.get('channel', 'Local Sync')}</div>", unsafe_allow_html=True)
                        
                        # Size details
                        size_str = ""
                        try:
                            detail_resp = requests.get(f"{BACKEND_URL}/playlist/detail/{song['filename']}")
                            if detail_resp.status_code == 200:
                                size_str = f"💾 Ukuran: **{detail_resp.json().get('size_mb', 0)} MB**"
                        except Exception:
                            pass
                        
                        if size_str:
                            st.markdown(f"<div style='font-size: 0.9rem; color: #CBD5E0; margin-bottom: 12px;'>{size_str}</div>", unsafe_allow_html=True)
                        
                        # Dynamic playback triggers
                        stream_col, server_col, playlist_col, delete_col = st.columns([2, 2, 2, 1])
                        
                        with stream_col:
                            # Stream in Browser using st.audio
                            audio_url = f"{BACKEND_URL}/stream/{song['filename']}"
                            st.audio(audio_url, format="audio/mpeg")
                            
                        with server_col:
                            # Play on Server
                            if st.button("📻 Putar di Server", key=f"server_play_{idx}"):
                                play_resp = requests.post(f"{BACKEND_URL}/play/{song['filename']}")
                                if play_resp.status_code == 200 and play_resp.json().get("status"):
                                    st.toast(f"▶ Memutar di server: {song['title']}")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("Gagal memutar di server.")
                                    
                        with playlist_col:
                            # Add to playlist custom
                            try:
                                playlists_resp = requests.get(f"{BACKEND_URL}/playlists")
                                if playlists_resp.status_code == 200:
                                    all_pl = playlists_resp.json().get("playlists", [])
                                    
                                    if all_pl:
                                        selected_pl = st.selectbox(
                                            "Tambahkan ke playlist:",
                                            ["Pilih playlist..."] + all_pl,
                                            key=f"pl_select_{idx}",
                                            label_visibility="collapsed"
                                        )
                                        if selected_pl != "Pilih playlist...":
                                            add_resp = requests.post(
                                                f"{BACKEND_URL}/playlists",
                                                json={"playlist_name": selected_pl, "song_filename": song["filename"]}
                                            )
                                            if add_resp.status_code == 200 and add_resp.json().get("status"):
                                                st.toast(f"✅ Dimasukkan ke playlist: '{selected_pl}'")
                                                time.sleep(0.5)
                                                st.rerun()
                                    else:
                                        st.caption("Buat playlist di tab 'Playlist Custom'")
                            except Exception:
                                pass
                                
                        with delete_col:
                            # Delete from Server
                            if st.button("🗑️ Hapus", key=f"delete_song_{idx}"):
                                del_resp = requests.delete(f"{BACKEND_URL}/playlist/{song['filename']}")
                                if del_resp.status_code == 200 and del_resp.json().get("status"):
                                    st.toast(f"🗑️ Lagu berhasil dihapus!")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("Gagal menghapus lagu.")
                                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Belum ada lagu yang diunduh. Silakan pergi ke tab 'Cari & Unduh Musik' untuk menambahkan lagu.")
        else:
            st.error("Gagal memuat daftar lagu dari backend.")
    except Exception as e:
        st.error(f"Koneksi backend gagal: {e}")

# =========================================
# MENU 3: CUSTOM PLAYLIST MANAGER
# =========================================
elif menu == "📂 Playlist Custom":
    st.markdown("<h2 style='font-weight: 700;'>📂 Manajemen Playlist Custom</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0AEC0;'>Buat, kelola, dan putar grup lagu Anda yang disimpan secara permanen di database SQLite.</p>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("<h3 style='font-weight:600;'>➕ Buat Playlist Baru</h3>", unsafe_allow_html=True)
        new_pl_name = st.text_input("Nama Playlist Baru:", placeholder="Contoh: Lagu Santai Sore")
        if st.button("Buat Playlist"):
            if new_pl_name:
                # We can initialize it by creating a dummy record, or we just instruct how to add a song.
                # In our backend API, playlist is created dynamically when the first song is added.
                # But to display it in the selectbox, let's add a song immediately or suggest it.
                # Let's see: to let them choose which song to add to start the playlist:
                try:
                    playlist_resp = requests.get(f"{BACKEND_URL}/playlist")
                    if playlist_resp.status_code == 200:
                        songs = playlist_resp.json().get("songs", [])
                        if songs:
                            song_filenames = [s["filename"] for s in songs]
                            song_titles = [s["title"] for s in songs]
                            selected_song_idx = st.selectbox(
                                "Pilih lagu pertama untuk playlist ini:",
                                range(len(songs)),
                                format_func=lambda i: song_titles[i]
                            )
                            if st.button("Tambahkan & Buat", key="create_pl_btn"):
                                first_song_file = song_filenames[selected_song_idx]
                                add_resp = requests.post(
                                    f"{BACKEND_URL}/playlists",
                                    json={"playlist_name": new_pl_name, "song_filename": first_song_file}
                                )
                                if add_resp.status_code == 200 and add_resp.json().get("status"):
                                    st.success(f"Playlist '{new_pl_name}' berhasil dibuat dengan lagu pertama!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Gagal membuat playlist.")
                        else:
                            st.warning("Silakan unduh lagu terlebih dahulu di tab pencarian.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Nama playlist tidak boleh kosong!")
                
    with col_right:
        st.markdown("<h3 style='font-weight:600;'>📁 Daftar Playlist Anda</h3>", unsafe_allow_html=True)
        try:
            playlists_resp = requests.get(f"{BACKEND_URL}/playlists")
            if playlists_resp.status_code == 200:
                all_pl = playlists_resp.json().get("playlists", [])
                
                if all_pl:
                    selected_pl_view = st.selectbox("Pilih Playlist untuk Dilihat/Dikelola:", all_pl)
                    
                    if selected_pl_view:
                        # Load songs in playlist
                        pl_detail_resp = requests.get(f"{BACKEND_URL}/playlists/{selected_pl_view}")
                        if pl_detail_resp.status_code == 200:
                            pl_songs = pl_detail_resp.json().get("songs", [])
                            
                            st.write(f"Playlist: **{selected_pl_view}** ({len(pl_songs)} Lagu)")
                            
                            # Delete playlist entirely button
                            if st.button("🚨 Hapus Seluruh Playlist ini", key="del_pl_all"):
                                del_pl_resp = requests.delete(f"{BACKEND_URL}/playlists/{selected_pl_view}")
                                if del_pl_resp.status_code == 200 and del_pl_resp.json().get("status"):
                                    st.success(f"Playlist '{selected_pl_view}' dihapus.")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Gagal menghapus playlist.")
                            
                            st.markdown("---")
                            
                            if pl_songs:
                                for s_idx, s_song in enumerate(pl_songs):
                                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                                    pl_col1, pl_col2 = st.columns([1, 4])
                                    
                                    with pl_col1:
                                        if s_song.get("thumbnail"):
                                            st.image(s_song["thumbnail"], use_column_width=True)
                                        else:
                                            st.markdown("<div style='height: 70px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.03); border-radius: 8px;'><span style='font-size: 2rem;'>🎵</span></div>", unsafe_allow_html=True)
                                            
                                    with pl_col2:
                                        st.markdown(f"<div style='font-size:1.1rem; font-weight:600; color:white;'>{s_song['title']}</div>", unsafe_allow_html=True)
                                        st.markdown(f"<div style='font-size:0.85rem; color:#A0AEC0;'>{s_song.get('channel', '')}</div>", unsafe_allow_html=True)
                                        
                                        # Play controls & Remove from playlist button
                                        act_col1, act_col2, act_col3 = st.columns([2, 2, 1])
                                        
                                        with act_col1:
                                            st.audio(f"{BACKEND_URL}/stream/{s_song['filename']}", format="audio/mpeg")
                                            
                                        with act_col2:
                                            if st.button("📻 Putar di Server", key=f"pl_server_play_{s_idx}"):
                                                play_resp = requests.post(f"{BACKEND_URL}/play/{s_song['filename']}")
                                                if play_resp.status_code == 200 and play_resp.json().get("status"):
                                                    st.toast(f"▶ Memutar di server: {s_song['title']}")
                                                    time.sleep(0.5)
                                                    st.rerun()
                                                    
                                        with act_col3:
                                            if st.button("❌ Lepas", key=f"remove_from_pl_{s_idx}"):
                                                rem_resp = requests.delete(f"{BACKEND_URL}/playlists/{selected_pl_view}/{s_song['filename']}")
                                                if rem_resp.status_code == 200 and rem_resp.json().get("status"):
                                                    st.toast("Lagu dilepas dari playlist.")
                                                    time.sleep(0.5)
                                                    st.rerun()
                                                    
                                    st.markdown("</div>", unsafe_allow_html=True)
                            else:
                                st.info("Playlist kosong.")
                else:
                    st.info("Anda belum memiliki playlist custom. Buat playlist baru di panel kiri.")
        except Exception as e:
            st.error(f"Gagal mengambil playlist: {e}")

# =========================================
# MENU 4: SERVER PHYSICAL CONTROLLER
# =========================================
elif menu == "⚙️ Kontrol Server Fisik":
    st.markdown("<h2 style='font-weight: 700;'>⚙️ Kontrol Fisik Speaker Server</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0AEC0;'>Gunakan menu ini untuk mengontrol pemutaran musik secara fisik pada speaker keras server (menggunakan pygame backend).</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    try:
        current_resp = requests.get(f"{BACKEND_URL}/current")
        if current_resp.status_code == 200:
            current_song = current_resp.json().get("current_song")
            
            if current_song:
                st.markdown(f"""
                <div style='text-align: center; padding: 20px;'>
                    <span style='font-size: 5rem; animation: pulse 2s infinite;'>📻</span>
                    <h2 style='color: white; margin-top: 15px;'>Sedang Diputar Secara Fisik:</h2>
                    <h1 style='color: #FF2E55; font-weight:700;'>{current_song}</h1>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; padding: 20px; color: #A0AEC0;'>
                    <span style='font-size: 5rem;'>💤</span>
                    <h2>Pemutar server fisik dalam keadaan mati/berhenti.</h2>
                </div>
                """, unsafe_allow_html=True)
                
            # Control buttons
            st.markdown("<br>", unsafe_allow_html=True)
            col_p, col_r, col_s = st.columns(3)
            
            with col_p:
                if st.button("⏸️ Jeda (Pause) Server", key="srv_pause"):
                    resp = requests.post(f"{BACKEND_URL}/pause")
                    if resp.status_code == 200:
                        st.toast("⏸️ Pemutaran fisik server dijeda.")
                        
            with col_r:
                if st.button("▶️ Lanjutkan (Resume) Server", key="srv_resume"):
                    resp = requests.post(f"{BACKEND_URL}/resume")
                    if resp.status_code == 200:
                        st.toast("▶️ Pemutaran fisik server dilanjutkan.")
                        
            with col_s:
                if st.button("⏹️ Hentikan (Stop) Server", key="srv_stop"):
                    resp = requests.post(f"{BACKEND_URL}/stop")
                    if resp.status_code == 200:
                        st.toast("⏹️ Pemutaran fisik server dihentikan.")
                        time.sleep(0.5)
                        st.rerun()
                        
        else:
            st.error("Gagal terhubung dengan server fisik.")
    except Exception as e:
        st.error(f"Gagal mengambil status server: {e}")
        
    st.markdown("</div>", unsafe_allow_html=True)
