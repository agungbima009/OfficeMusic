# 🎵 Dokumentasi API - YouTube Music & Player Server

Dokumentasi ini berisi panduan lengkap penggunaan API untuk sistem **YouTube Music API & Player Server**. Seluruh endpoint di bawah ini dibangun menggunakan framework **FastAPI** (Python).

---

## 📌 Informasi Server Umum
* **Base URL**: `http://localhost:8000` (atau `http://127.0.0.1:8000`)
* **Format Request/Response**: Secara default menggunakan `application/json` (kecuali endpoint streaming audio).
* **Port Default**: `8000`
* **Folder Penyimpanan Cache**:
  * **Audio (`.mp3`)**: `music_cache/`
  * **Video (`.mp4`)**: `video_cache/`

---

## 🧭 Ringkasan Endpoint

| No | Kategori | Method | Endpoint | Fungsi / Deskripsi |
|---|---|---|---|---|
| 1 | **Umum** | `GET` | `/` | Cek status kesehatan server (Health Check) |
| 2 | **YouTube** | `POST` | `/youtube/search` | Mencari lagu/video musik di YouTube |
| 3 | **YouTube** | `POST` | `/youtube/download-audio` | Mengunduh audio YouTube ke server (`.mp3`) |
| 4 | **YouTube** | `POST` | `/youtube/download-video` | Mengunduh video YouTube ke server (`.mp4`) |
| 5 | **Playlist** | `GET` | `/playlist` | Melihat semua daftar lagu (`.mp3`) di server |
| 6 | **Playlist** | `GET` | `/playlist/detail/{filename}` | Melihat info detail file (ukuran MB) |
| 7 | **Playlist** | `DELETE`| `/playlist/{filename}` | Menghapus file lagu dari server |
| 8 | **Playlist** | `GET` | `/stream/{filename}` | Melakukan streaming/download file audio |
| 9 | **Player** | `POST` | `/play/{song_name}` | Memutar lagu secara fisik di server |
| 10 | **Player** | `POST` | `/pause` | Menjeda pemutaran musik sementara |
| 11 | **Player** | `POST` | `/resume` | Melanjutkan kembali lagu yang dijeda |
| 12 | **Player** | `POST` | `/stop` | Menghentikan pemutaran musik total |
| 13 | **Player** | `GET` | `/current` | Melihat lagu yang sedang diputar saat ini |

---

## 🛠️ Rincian Lengkap Endpoint

### 1. General & Health Check

#### **`GET /` (Health Check)**
Digunakan untuk memverifikasi apakah server API berjalan dengan lancar.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Request Body:** Tidak ada (None)
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "message": "API Running"
  }
  ```

---

### 2. Fitur YouTube (`/youtube`)

#### **`POST /youtube/search` (Pencarian Musik)**
Mencari lagu di YouTube berdasarkan query teks. Mengembalikan daftar informasi video lagu dari YouTube API.

* **Headers:**
  ```http
  Content-Type: application/json
  Accept: application/json
  ```
* **Request Body (JSON):**
  * `query` (string, required): Kata kunci pencarian (judul lagu atau penyanyi).
  ```json
  {
    "query": "Coke Bottle Agnez Mo"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "results": [
      {
        "title": "AGNEZ MO - Coke Bottle ft. Timbaland, T.I. (Official Music Video)",
        "channel": "AGNEZ MO",
        "thumbnail": "https://i.ytimg.com/vi/h8D-pLkuWj4/hqdefault.jpg",
        "url": "https://www.youtube.com/watch?v=h8D-pLkuWj4"
      }
    ]
  }
  ```

#### **`POST /youtube/download-audio` (Unduh MP3)**
Mengunduh audio dari YouTube dan mengubah formatnya menjadi `.mp3` 192kbps menggunakan `yt-dlp` dan `ffmpeg`. File disimpan di folder `music_cache`.

* **Headers:**
  ```http
  Content-Type: application/json
  Accept: application/json
  ```
* **Request Body (JSON):**
  * Harus mengirim objek data video (biasanya didapat dari hasil `/youtube/search`).
  * Minimal menyertakan `title` dan `url`.
  ```json
  {
    "title": "AGNEZ MO - Coke Bottle ft. Timbaland, T.I. (Official Music Video)",
    "url": "https://www.youtube.com/watch?v=h8D-pLkuWj4"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "cached": false,
    "file_path": "music_cache\\AGNEZ_MO_Coke_Bottle_ft_Timbaland_T_I_Official_Music_Video.mp3"
  }
  ```
  > 💡 **Info Cache**: Jika file sudah pernah diunduh sebelumnya, server akan langsung mengembalikan `"cached": true` secara instan tanpa perlu mengunduh ulang dari YouTube.

#### **`POST /youtube/download-video` (Unduh MP4)**
Mengunduh video utuh (audio + video) dari YouTube dan menyimpannya dalam format `.mp4` berkualitas tinggi di folder `video_cache`.

* **Headers:**
  ```http
  Content-Type: application/json
  Accept: application/json
  ```
* **Request Body (JSON):**
  ```json
  {
    "title": "AGNEZ MO - Coke Bottle ft. Timbaland, T.I. (Official Music Video)",
    "url": "https://www.youtube.com/watch?v=h8D-pLkuWj4"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "cached": false,
    "file_path": "video_cache\\AGNEZ_MO_Coke_Bottle_ft_Timbaland_T_I_Official_Music_Video.mp4"
  }
  ```

---

### 3. Fitur Playlist

#### **`GET /playlist` (Daftar Lagu Lokal)**
Mengambil seluruh nama file lagu berformat `.mp3` yang ada di server.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Request Body:** Tidak ada (None)
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "total": 2,
    "songs": [
      "AGNEZ_MO_Coke_Bottle_ft_Timbaland_T_I_Official_Music_Video.mp3",
      "Katy_Perry_Roar.mp3"
    ]
  }
  ```

#### **`GET /playlist/detail/{filename}` (Detail Ukuran Lagu)**
Mengambil info ukuran file dalam Megabyte (MB) dari file `.mp3` yang terspesifikasi.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Path Parameters:**
  * `filename` (string, required): Nama file lagu (misal: `Katy_Perry_Roar.mp3`).
* **Request Body:** Tidak ada (None)
* **Response Success (200 OK):**
  ```json
  {
    "status": true,
    "filename": "Katy_Perry_Roar.mp3",
    "size_mb": 4.52
  }
  ```
* **Response Error (404 Not Found / File Tidak Ada):**
  ```json
  {
    "status": false,
    "message": "File not found"
  }
  ```

#### **`DELETE /playlist/{filename}` (Hapus Lagu)**
Menghapus file lagu `.mp3` secara permanen dari server.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Path Parameters:**
  * `filename` (string, required): Nama file lagu yang ingin dihapus.
* **Request Body:** Tidak ada (None)
* **Response Success (200 OK):**
  ```json
  {
    "status": true,
    "message": "Katy_Perry_Roar.mp3 deleted"
  }
  ```
* **Response Error (404 Not Found):**
  ```json
  {
    "status": false,
    "message": "File not found"
  }
  ```

#### **`GET /stream/{filename}` (Streaming Audio)**
Endpoint khusus untuk streaming musik secara real-time. Memutar file langsung di tag audio HTML5 atau media player eksternal.

* **Headers:**
  ```http
  Accept: audio/mpeg
  ```
* **Path Parameters:**
  * `filename` (string, required): Nama file lagu (misal: `Katy_Perry_Roar.mp3`).
* **Request Body:** Tidak ada (None)
* **Response (200 OK - Binary Stream):**
  * Mengembalikan file audio stream dengan header `Content-Type: audio/mpeg` untuk pemutaran langsung.

---

### 4. Fitur Player Controller (Pemutaran Fisik Server)

Fitur ini menggunakan library `pygame` untuk memainkan musik secara fisik pada speaker hardware server (cocok untuk proyek smart-home, kantor, atau pemutar musik IoT).

#### **`POST /play/{song_name}` (Putar Musik di Server)**
Memutar file musik lokal server secara fisik melalui speaker server. Jika ada lagu lain yang sedang berputar, lagu tersebut akan otomatis dihentikan terlebih dahulu.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Path Parameters:**
  * `song_name` (string, required): Nama file lagu (misal: `Katy_Perry_Roar.mp3`).
* **Request Body:** Tidak ada (None)
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "message": "Playing Katy_Perry_Roar.mp3"
  }
  ```

#### **`POST /pause` (Jeda Musik)**
Menjeda pemutaran musik fisik di server sementara waktu.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Request Body:** Tidak ada (None)
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "message": "Music paused"
  }
  ```

#### **`POST /resume` (Lanjutkan Musik)**
Melanjutkan kembali pemutaran musik fisik di server yang sebelumnya dijeda (`pause`).

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Request Body:** Tidak ada (None)
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "message": "Music resumed"
  }
  ```

#### **`POST /stop` (Hentikan Pemutaran)**
Menghentikan pemutaran musik fisik secara total di server.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Request Body:** Tidak ada (None)
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "message": "Music stopped"
  }
  ```

#### **`GET /current` (Cek Lagu Berputar)**
Mendapatkan nama file lagu yang sedang diputar di server saat ini.

* **Headers:**
  ```http
  Accept: application/json
  ```
* **Request Body:** Tidak ada (None)
* **Response (200 OK):**
  ```json
  {
    "status": true,
    "current_song": "Katy_Perry_Roar.mp3"
  }
  ```
  > ℹ️ **Catatan**: Field `current_song` akan bernilai `null` jika pemutar server dalam keadaan mati/berhenti.

---

## 💡 Contoh Pengujian Cepat (Menggunakan `curl`)

Berikut adalah beberapa contoh pemanggilan API menggunakan CLI `curl` untuk memudahkan developer melakukan pengujian:

1. **Uji Coba Health Check:**
   ```bash
   curl -X GET http://localhost:8000/
   ```

2. **Mencari Lagu:**
   ```bash
   curl -X POST http://localhost:8000/youtube/search \
     -H "Content-Type: application/json" \
     -d '{"query": "Coldplay Yellow"}'
   ```

3. **Mendownload MP3:**
   ```bash
   curl -X POST http://localhost:8000/youtube/download-audio \
     -H "Content-Type: application/json" \
     -d '{"title": "Coldplay - Yellow", "url": "https://www.youtube.com/watch?v=yKNxeF4KMsY"}'
   ```

4. **Melihat Playlist Lokal:**
   ```bash
   curl -X GET http://localhost:8000/playlist
   ```

5. **Memainkan Lagu Melalui Speaker Server:**
   ```bash
   curl -X POST http://localhost:8000/play/Coldplay_-_Yellow.mp3
   ```

---
*Dokumentasi ini dibuat otomatis untuk membantu visualisasi dan integrasi Client Application (Mobile/Web) ke backend Office Musik Server.*
