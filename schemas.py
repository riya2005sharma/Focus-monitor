from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str

class SessionCreate(BaseModel):
    subject: str
    planned_duration: int

class SessionEnd(BaseModel):
    session_id: int
    actual_duration: int
    status: str
    focus_score: float = 0.0