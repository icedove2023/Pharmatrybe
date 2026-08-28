"""Authenticated identity schema for the PharmaTrybe backend."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.auth.roles import PharmaTrybeRole


class AuthenticatedUser(BaseModel):
    """Verified Supabase identity before application membership resolution."""

    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., min_length=1)
    email: str = Field(default="")
    role: PharmaTrybeRole | str | None = Field(default=None)
    active: bool = Field(default=True)
