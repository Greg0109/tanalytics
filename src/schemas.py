from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserProfile(BaseModel):
    """Internal representation of a Twitch user profile."""

    id: str = Field(..., description="User ID")
    login: str = Field(..., description="Login name")
    display_name: str = Field(..., description="Display name")
    type: str = Field(..., description="User type: 'staff', 'admin', 'global_mod', or ''")
    description: str = Field(..., description="Channel description")
    broadcaster_type: str = Field(..., description="Broadcaster type: 'partner', 'affiliate', or ''")
    profile_image_url: str = Field(..., description="Profile image URL")
    offline_image_url: str = Field(..., description="Offline image URL")
    view_count: int = Field(..., description="Total channel views")
    created_at: datetime = Field(..., description="Account creation date")


class Stream(BaseModel):
    """Internal representation of an active Twitch stream."""

    id: str = Field(..., description="Stream ID")
    title: str = Field(..., description="Stream title")
    viewer_count: int = Field(..., description="Current viewers")
    user_id: str = Field(..., description="Streamer user ID")
    user_login: str = Field(..., description="Streamer login name")
    user_name: str = Field(..., description="Streamer display name")
    started_at: datetime = Field(..., description="Stream start time")
    language: str = Field(..., description="Stream language")
    thumbnail_url: str = Field(..., description="Thumbnail URL")
    game_id: Optional[str] = Field(None, description="Game ID")
    game_name: Optional[str] = Field(None, description="Game name")


class UserQuery(BaseModel):
    """Query a Twitch user by ID or login."""

    id: Optional[str] = Field(None, description="User ID")
    login: Optional[str] = Field(None, description="Login name")


class UserResponse(BaseModel):
    """API response for a single Twitch user."""

    user: UserProfile


class StreamQuery(BaseModel):
    """Query active streams by user ID or login."""

    user_id: Optional[str] = Field(None, description="User ID")
    user_login: Optional[str] = Field(None, description="Login name")


class StreamsResponse(BaseModel):
    """API response for active Twitch streams."""

    streams: List[Stream]
