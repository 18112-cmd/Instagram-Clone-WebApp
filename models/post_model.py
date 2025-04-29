from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PostBase(BaseModel):
    caption: str

class PostCreate(PostBase):
    """Used when creating a new post."""
    image_data: bytes
    content_type: str

class PostInDB(PostBase):
    """Post stored in Firestore."""
    Username: str
    Date: datetime
    image_url: str

class CommentCreate(BaseModel):
    """When a user adds a comment."""
    post_id: str
    comment: str

class CommentInDB(BaseModel):
    """Comment stored inside a Post's Comments subcollection."""
    username: str
    comment: str
    date: datetime
