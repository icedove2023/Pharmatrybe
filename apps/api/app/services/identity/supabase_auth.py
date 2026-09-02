"""Server-only Supabase Auth invitation integration."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class SupabaseAuthError(RuntimeError):
    """Raised when Supabase Auth cannot create an invitation."""


def invite_user_by_email(email: str) -> str:
    """Ask Supabase Auth to create and email an invitation."""
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SupabaseAuthError("Supabase Auth invitation delivery is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    if not settings.invitation_frontend_route:
        raise SupabaseAuthError("Supabase Auth invitation redirect is not configured. Set INVITATION_FRONTEND_ROUTE.")

    try:
        response = httpx.post(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/admin/invite",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "Content-Type": "application/json",
            },
            json={"email": email, "redirect_to": settings.invitation_frontend_route},
            timeout=settings.default_timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAuthError("Supabase Auth invitation service is unavailable") from exc
    if response.is_error:
        try:
            detail: Any = response.json() if response.content else None
        except ValueError:
            detail = None
        message = detail.get("msg") or detail.get("message") if isinstance(detail, dict) else None
        raise SupabaseAuthError(message or "Supabase Auth rejected the invitation")
    try:
        user_id = response.json().get("id")
    except (ValueError, TypeError) as exc:
        raise SupabaseAuthError("Supabase Auth returned an invalid invitation response") from exc
    if not user_id:
        raise SupabaseAuthError("Supabase Auth did not return an invited user ID")
    return str(user_id)