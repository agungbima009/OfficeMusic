# =========================================
# YOUTUBE MUSIC PLAYER GUI
# =========================================
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkhtmlview import HTMLLabel

from googleapiclient.discovery import build

import yt_dlp
import threading
import requests
import pygame
import io
import os
import re

from dotenv import load_dotenv

# =========================================
# LOAD ENV
# =========================================
load_dotenv()

API_KEY = os.getenv("YOUR_API_KEY")

if not API_KEY:

    raise ValueError(
        "YouTube API KEY not found in .env"
    )

# =========================================
# CONFIG
# =========================================
MAX_RESULTS = 7

DOWNLOAD_FOLDER = "music_cache"

os.makedirs(
    DOWNLOAD_FOLDER,
    exist_ok=True
)

VIDEO_FOLDER = "video_cache"

os.makedirs(
    VIDEO_FOLDER,
    exist_ok=True
)

# =========================================
# INIT PYGAME
# =========================================
pygame.mixer.init()

# =========================================
# CLEAN FILENAME
# =========================================
def safe_filename(text):

    return re.sub(
        r'[\\/*?:"<>|]',
        "",
        text
    )

# =========================================
# SEARCH MUSIC
# =========================================
def youtube_search_music(query):

    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )

    response = youtube.search().list(

        q=query,

        part="id,snippet",

        type="video",

        maxResults=MAX_RESULTS,

        topicId="/m/04rlf"

    ).execute()

    videos = []

    for item in response.get("items", []):

        video_id = item["id"]["videoId"]

        videos.append({

            "title":
                item["snippet"]["title"],

            "channel":
                item["snippet"]["channelTitle"],

            "thumbnail":
                item["snippet"]["thumbnails"]["high"]["url"],

            "url":
                f"https://www.youtube.com/watch?v={video_id}"

        })

    return videos

# =========================================
# DOWNLOAD AUDIO
# =========================================
def download_audio(video):

    title = safe_filename(
        video['title']
    )

    output_mp3 = os.path.join(
        DOWNLOAD_FOLDER,
        f"{title}.mp3"
    )

    # =====================================
    # CACHE CHECK
    # =====================================
    if os.path.exists(output_mp3):

        return output_mp3, True

    # =====================================
    # DOWNLOAD
    # =====================================
    ydl_opts = {

        'format':
            'bestaudio/best',

        'outtmpl':
            os.path.join(
                DOWNLOAD_FOLDER,
                f"{title}.%(ext)s"
            ),

        'quiet':
            True,

        'noplaylist':
            True,

        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        },

        'postprocessors': [{

            'key':
                'FFmpegExtractAudio',

            'preferredcodec':
                'mp3',

            'preferredquality':
                '192',

        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        ydl.download(
            [video['url']]
        )

    return output_mp3, False

# =========================================
# DOWNLOAD VIDEO
# =========================================
def download_video(video):

    title = safe_filename(
        video['title']
    )

    output_mp4 = os.path.join(
        VIDEO_FOLDER,
        f"{title}.mp4"
    )

    # =====================================
    # CACHE CHECK
    # =====================================
    if os.path.exists(output_mp4):

        return output_mp4, True

    ydl_opts = {

        'format':
            'bestvideo+bestaudio/best',

        'outtmpl':
            os.path.join(
                VIDEO_FOLDER,
                f"{title}.%(ext)s"
            ),

        'quiet':
            True,

        'noplaylist':
            True,

        'merge_output_format':
            'mp4',

        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        ydl.download(
            [video['url']]
        )

    return output_mp4, False

# =========================================
# PLAY AUDIO
# =========================================
def play_audio(audio_path):

    pygame.mixer.music.stop()

    pygame.mixer.music.load(
        audio_path
    )

    pygame.mixer.music.play()

# =========================================
# PLAY VIDEO
# =========================================
def play_video(video_path):

    subprocess.Popen(
        [video_path],
        shell=True
    )

# =========================================
# STOP AUDIO
# =========================================
def stop_audio():

    pygame.mixer.music.stop()

# =========================================
# GUI CLASS
# =========================================
class MusicPlayerGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "YouTube Music Player"
        )

        self.root.geometry(
            "1300x900"
        )

        self.root.configure(
            bg="#0f0f0f"
        )

        self.results = []

        self.thumbnail_refs = []

        # =====================================
        # TITLE
        # =====================================
        title = tk.Label(

            root,

            text="YouTube Music Player",

            font=("Arial", 34, "bold"),

            bg="#0f0f0f",

            fg="#ff0000"

        )

        title.pack(
            pady=20
        )

        # =====================================
        # SEARCH FRAME
        # =====================================
        search_frame = tk.Frame(

            root,

            bg="#0f0f0f"
        )

        search_frame.pack(
            pady=10
        )

        self.search_entry = tk.Entry(

            search_frame,

            width=45,

            font=("Arial", 16),

            bg="#1e1e1e",

            fg="white",

            insertbackground="white",

            relief="flat"
        )

        self.search_entry.pack(

            side=tk.LEFT,

            padx=10,

            ipady=10
        )

        search_button = tk.Button(

            search_frame,

            text="Search",

            font=("Arial", 14, "bold"),

            bg="#ff0000",

            fg="white",

            relief="flat",

            padx=25,

            pady=10,

            command=self.search_music
        )

        search_button.pack(
            side=tk.LEFT
        )

        # =====================================
        # STATUS
        # =====================================
        self.status_label = tk.Label(

            root,

            text="Ready",

            font=("Arial", 11),

            bg="#0f0f0f",

            fg="#aaaaaa"
        )

        self.status_label.pack(
            pady=10
        )

        # =====================================
        # VIDEO PREVIEW
        # =====================================
        self.video_frame = tk.Frame(
            root,
            bg="#0f0f0f"
        )

        self.video_frame.pack(
            pady=10
        )

        self.video_preview = HTMLLabel(

            self.video_frame,

            html="""
            <div style='
                color:white;
                font-size:20px;
                padding:20px;
            '>
            No music playing
            </div>
            """,

            background="#0f0f0f"
        )

        self.video_preview.pack()

        # =====================================
        # SCROLLABLE AREA
        # =====================================
        self.canvas = tk.Canvas(

            root,

            bg="#0f0f0f",

            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(

            root,

            orient="vertical",

            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(

            self.canvas,

            bg="#0f0f0f"
        )

        self.scrollable_frame.bind(

            "<Configure>",

            lambda e:
                self.canvas.configure(
                    scrollregion=
                    self.canvas.bbox("all")
                )
        )

        self.canvas.create_window(

            (0, 0),

            window=self.scrollable_frame,

            anchor="nw"
        )

        self.canvas.configure(

            yscrollcommand=
                self.scrollbar.set
        )

        self.canvas.pack(

            side="left",

            fill="both",

            expand=True,

            padx=10,

            pady=10
        )

        self.scrollbar.pack(

            side="right",

            fill="y"
        )

        # =====================================
        # STOP BUTTON
        # =====================================
        stop_btn = tk.Button(

            root,

            text="■ Stop Music",

            font=("Arial", 14, "bold"),

            bg="#444444",

            fg="white",

            relief="flat",

            padx=20,

            pady=10,

            command=self.stop_music
        )

        stop_btn.pack(
            pady=15
        )

    # =========================================
    # VIDEO MODE
    # =========================================
    def play_video_mode(self, video):

        def run():

            try:

                self.status_label.config(
                    text=f"Preparing video: {video['title']}"
                )

                video_file, cached = download_video(
                    video
                )

                if cached:

                    self.status_label.config(
                        text="Playing cached video..."
                    )

                else:

                    self.status_label.config(
                        text="Downloaded & playing video..."
                    )

                # =================================
                # VIDEO PREVIEW
                # =================================
                video_html = f"""
                <div style="
                    background:#1e1e1e;
                    padding:15px;
                    border-radius:15px;
                    width:850px;
                ">

                    <img src="{video['thumbnail']}"
                         width="700">

                    <h2 style="color:white;">
                        {video['title']}
                    </h2>

                    <p style="color:gray;">
                        {video['channel']}
                    </p>

                    <a href="{video['url']}"
                       style="
                            color:red;
                            font-size:18px;
                       ">
                       Open in YouTube
                    </a>

                </div>
                """

                self.video_preview.set_html(
                    video_html
                )

                # =================================
                # PLAY VIDEO
                # =================================
                play_video(video_file)

            except Exception as e:

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        threading.Thread(
            target=run,
            daemon=True
        ).start()

    # =========================================
    # SEARCH MUSIC
    # =========================================
    def search_music(self):

        query = self.search_entry.get()

        if not query:

            messagebox.showwarning(
                "Warning",
                "Enter music title."
            )

            return

        self.status_label.config(
            text="Searching..."
        )

        # clear old
        for widget in self.scrollable_frame.winfo_children():

            widget.destroy()

        def run_search():

            try:

                self.results = youtube_search_music(
                    query
                )

                self.thumbnail_refs.clear()

                for video in self.results:

                    self.create_music_card(
                        video
                    )

                self.status_label.config(
                    text=f"Found {len(self.results)} music."
                )

            except Exception as e:

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        threading.Thread(
            target=run_search,
            daemon=True
        ).start()

    # =========================================
    # CREATE MUSIC CARD
    # =========================================
    def create_music_card(self, video):

        # =====================================
        # DOWNLOAD THUMBNAIL
        # =====================================
        response = requests.get(
            video['thumbnail']
        )

        image_data = response.content

        image = Image.open(
            io.BytesIO(image_data)
        )

        image = image.resize(
            (180, 100)
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self.thumbnail_refs.append(
            photo
        )

        # =====================================
        # CARD
        # =====================================
        card = tk.Frame(

            self.scrollable_frame,

            bg="#1e1e1e",

            padx=15,

            pady=15
        )

        card.pack(

            fill="x",

            padx=10,

            pady=10
        )

        # =====================================
        # IMAGE
        # =====================================
        img_label = tk.Label(

            card,

            image=photo,

            bg="#1e1e1e"
        )

        img_label.pack(
            side=tk.LEFT
        )

        # =====================================
        # INFO FRAME
        # =====================================
        info_frame = tk.Frame(

            card,

            bg="#1e1e1e"
        )

        info_frame.pack(

            side=tk.LEFT,

            padx=20,

            fill="x",

            expand=True
        )

        # =====================================
        # TITLE
        # =====================================
        title_label = tk.Label(

            info_frame,

            text=video['title'],

            font=("Arial", 15, "bold"),

            fg="white",

            bg="#1e1e1e",

            wraplength=650,

            justify="left"
        )

        title_label.pack(
            anchor="w"
        )

        # =====================================
        # CHANNEL
        # =====================================
        channel_label = tk.Label(

            info_frame,

            text=video['channel'],

            font=("Arial", 11),

            fg="#aaaaaa",

            bg="#1e1e1e"
        )

        channel_label.pack(
            anchor="w",
            pady=8
        )

        # =====================================
        # BUTTON FRAME
        # =====================================
        button_frame = tk.Frame(
            card,
            bg="#1e1e1e"
        )

        button_frame.pack(
            side=tk.RIGHT,
            padx=10
        )

        # =====================================
        # AUDIO BUTTON
        # =====================================
        audio_btn = tk.Button(

            button_frame,

            text="🎵 Audio",

            font=("Arial", 11, "bold"),

            bg="#ff0000",

            fg="white",

            relief="flat",

            padx=15,

            pady=10,

            command=lambda:
                self.play_music(
                    video,
                    audio_btn
                )
        )

        audio_btn.pack(
            pady=5
        )

        # =====================================
        # VIDEO BUTTON
        # =====================================
        video_btn = tk.Button(

            button_frame,

            text="🎬 Video",

            font=("Arial", 11, "bold"),

            bg="#1db954",

            fg="white",

            relief="flat",

            padx=15,

            pady=10,

            command=lambda:
                self.play_video_mode(
                    video
                )
        )

        video_btn.pack(
            pady=5
        )

    # =========================================
    # PLAY MUSIC
    # =========================================
    def play_music(self, video, button):

        def run():

            try:

                self.status_label.config(
                    text=f"Preparing: {video['title']}"
                )

                # =================================
                # DOWNLOAD / CACHE
                # =================================
                audio_file, cached = download_audio(
                    video
                )

                if cached:

                    self.status_label.config(
                        text="Playing cached audio..."
                    )

                else:

                    self.status_label.config(
                        text="Downloaded & playing..."
                    )

                    button.config(
                        text="▶ Play"
                    )

                # =================================
                # VIDEO PREVIEW
                # =================================
                video_html = f"""
                <div style="
                    background:#1e1e1e;
                    padding:15px;
                    border-radius:15px;
                    width:850px;
                ">

                    <img src="{video['thumbnail']}"
                         width="700">

                    <h2 style="color:white;">
                        {video['title']}
                    </h2>

                    <p style="color:gray;">
                        {video['channel']}
                    </p>

                    <a href="{video['url']}"
                       style="
                            color:red;
                            font-size:18px;
                       ">
                       Open in YouTube
                    </a>

                </div>
                """

                self.video_preview.set_html(
                    video_html
                )

                # =================================
                # PLAY AUDIO
                # =================================
                play_audio(audio_file)

            except Exception as e:

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        threading.Thread(
            target=run,
            daemon=True
        ).start()

    # =========================================
    # STOP MUSIC
    # =========================================
    def stop_music(self):

        stop_audio()

        self.status_label.config(
            text="Stopped"
        )

# =========================================
# MAIN
# =========================================
def main():

    root = tk.Tk()

    app = MusicPlayerGUI(root)

    root.mainloop()

# =========================================
# RUN
# =========================================
if __name__ == "__main__":

    main()