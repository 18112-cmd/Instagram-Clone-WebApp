from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    """Used when creating a new user."""
    pass

class UserInDB(UserBase):
    """User data stored in Firestore."""
    followers: List[str] = []
    following: List[str] = []
    created_at: datetime

class FollowAction(BaseModel):
    """Follow or Unfollow a user."""
    target_user_id: str
