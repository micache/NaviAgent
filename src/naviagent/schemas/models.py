"""Pydantic models for API requests and responses.

We model only the fields used by the API. Supabase table columns are shown in
the provided ERD image: users, trips, chat_sessions, chat_messages and
auth.users (managed by Supabase Auth). We don't store passwords directly.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field

#Database models
class UserProfile(BaseModel):
    user_id: str
    created_at: Optional[datetime] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    average_budget: Optional[int] = None


class Trip(BaseModel):
    id: str
    user_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    address: Optional[Any] = None  # Can be dict or string
    status: Optional[str] = None

class ChatSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    update_at: Optional[datetime] = None


class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    role: str
    content: str
    created_at: Optional[datetime] = None

class Plans(BaseModel):
    id : Optional[str] = None
    user_id : str
    destination : str
    departure: str
    start_date : date
    duration : int
    number_of_travelers : int
    budget : Optional[int] = None
    travel_style : Optional[str] = None
    notes: Optional[str] = None
    guide_book: Optional[str] = None
    
# API request/response models

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="User password for Supabase auth")
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    average_budget: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LogoutResponse(BaseModel):
    success: bool



class CreateTripRequest(BaseModel):
    address: Any  # Can be dict {name, lat, lng} or string
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = "visited"


class CreateMessageRequest(BaseModel):
    role: str
    content: str
