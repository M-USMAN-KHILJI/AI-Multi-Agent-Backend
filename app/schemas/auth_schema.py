import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class UserSignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: str = Field(..., description="Valid email address (e.g. user@gmail.com)")
    password: str = Field(..., min_length=6, max_length=128, description="Account password")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Username must be at least 2 characters.")
        return trimmed

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        email = v.strip().lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Please enter a valid email address (e.g. yourname@gmail.com).")
        return email

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v

class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Email address or username")
    password: str = Field(..., description="Account password")

class GoogleAuthRequest(BaseModel):
    email: str = Field(..., description="Google Account email")
    name: Optional[str] = Field(default="Google User", description="User's full name from Google")
    uid: Optional[str] = Field(default=None, description="Firebase User UID")
    photo_url: Optional[str] = Field(default=None, description="Google profile picture URL")
    is_signup: Optional[bool] = Field(default=False, description="Flag indicating if request came from signup page")

class UserAuthResponse(BaseModel):
    id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    token: str
    message: str
