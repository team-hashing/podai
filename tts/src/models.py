from pydantic import BaseModel

class Podcast(BaseModel):
    user_id: str
    podcast_name: str
    script: dict