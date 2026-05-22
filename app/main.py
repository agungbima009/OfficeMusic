from fastapi import FastAPI

from app.routes.youtube_routes import router as youtube_router
from app.routes.playlist_routes import router as playlist_router
from app.routes.player_routes import router as player_router
from app.core.database import init_db

app = FastAPI(
    title="YouTube Music API"
)

@app.on_event("startup")
def on_startup():
    init_db()


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
    tags=["Player"]
)

@app.get("/")
def home():

    return {
        "status": True,
        "message": "API Running"
    }