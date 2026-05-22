from pydantic import BaseModel

class VideoRequest(BaseModel):

    title: str

    url: str

    channel: str = ""

    thumbnail: str = ""

class SearchRequest(BaseModel):

    query: str