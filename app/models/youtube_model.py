from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str

class VideoData(BaseModel):
    title: str
    channel: str
    thumbnail: str
    url: str