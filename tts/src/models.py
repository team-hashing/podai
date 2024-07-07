from pydantic import BaseModel, Field

class Podcast(BaseModel):
    user_id: str
    podcast_name: str
    podcast_id: str