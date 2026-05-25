from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.youtube_routes import router as youtube_router
from app.routes.playlist_routes import router as playlist_router
from app.routes.player_routes import router as player_router
from app.core.database import init_db


# =========================================================
# LIFESPAN (pengganti @app.on_event yang sudah deprecated)
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (opsional: tambahkan cleanup di sini)


app = FastAPI(
    title="YouTube Music API",
    lifespan=lifespan
)


# =========================================================
# CORS MIDDLEWARE
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # ganti dengan domain frontend di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================
app.include_router(
    youtube_router,
    prefix="/youtube",
    tags=["YouTube"]
)

app.include_router(
    playlist_router,
    tags=["Playlist"]
)

app.include_router(
    player_router,
    prefix="/player",
    tags=["Player"]
)


# =========================================================
# ROOT
# =========================================================
@app.get("/")
def home():
    return {
        "status": True,
        "message": "API Running"
    }