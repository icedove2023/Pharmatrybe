"""Server-only Supabase Auth invitation integration."""

from __future__ import annotations

import secrets
import string
from typing import Any

import httpx

from app.core.config import settings


def generate_temporary_password(length: int = 12) -> str:
    """Generate a random, secure default password for an invited professional.

    The invited user is expected to change this on first login (the Settings
    screen enforces this via ProfessionalProfile.force_password_reset). We never
    persist this value anywhere - it is returned once, in the invite API response,
    so the inviting admin can share it with the invited professional.
    """
    alphabet_upper = string.ascii_uppercase
    alphabet_lower = string.ascii_lowercase
    alphabet_digits = string.digits
    alphabet_symbols = "!@#$%^&*"
    # Guarantee at least one of each character class, then fill the rest randomly.
    required = [
        secrets.choice(alphabet_upper),
        secrets.choice(alphabet_lower),
        secrets.choice(alphabet_digits),
        secrets.choice(alphabet_symbols),
    ]
    remaining_alphabet = alphabet_upper + alphabet_lower + alphabet_digits
    remaining = [secrets.choice(remaining_alphabet) for _ in range(max(length - len(required), 0))]
    password_chars = required + remaining
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def set_user_password(user_id: str, password: str) -> None:
    """Set a Supabase Auth user's password directly via the Admin API.

    Also confirms the user's email, since we are handing them working
    credentials out of band (a shared temporary password) rather than
    relying on the invite email's magic link to establish their session.
    """
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SupabaseAuthError("Supabase Auth invitation delivery is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    try:
        response = httpx.put(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/admin/users/{user_id}",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "Content-Type": "application/json",
            },
            json={"password": password, "email_confirm": True},
            timeout=settings.default_timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAuthError("Supabase Auth is unavailable while setting the temporary password") from exc
    if response.is_error:
        raise SupabaseAuthError(
            f"Supabase Auth rejected setting the temporary password "
            f"(HTTP {response.status_code}): {response.text or 'no response body'}"
        )


class SupabaseAuthError(RuntimeError):
    """Raised when Supabase Auth cannot create an invitation."""


def is_email_confirmed(user_id: str) -> bool:
    """Check whether a Supabase Auth user has confirmed their email address.

    Used server-side as a hard gate before completing hospital registration,
    so verification is enforced by our own API regardless of whether the
    Supabase project's "Confirm email" dashboard setting is also enabled.
    """
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SupabaseAuthError("Supabase Auth is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    try:
        response = httpx.get(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/admin/users/{user_id}",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
            },
            timeout=settings.default_timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAuthError("Supabase Auth is unavailable while checking email verification status") from exc
    if response.is_error:
        raise SupabaseAuthError(
            f"Supabase Auth rejected the email verification check "
            f"(HTTP {response.status_code}): {response.text or 'no response body'}"
        )
    try:
        payload = response.json()
    except ValueError as exc:
        raise SupabaseAuthError("Supabase Auth returned an invalid user lookup response") from exc
    return bool(payload.get("email_confirmed_at") or payload.get("confirmed_at"))


def invite_user_by_email(email: str, hospital_name: str | None = None) -> tuple[str, str]:
    """Ask Supabase Auth to create and email an invitation.

    Also sets a generated temporary password on the new account (see
    set_user_password) so the invited professional can sign in directly at
    the normal login page with email + temporary password, without
    depending on the magic-link email actually arriving. Returns
    (supabase_user_id, temporary_password).

    hospital_name is passed through as template data ({{ .Data.hospital_name }})
    so the "Invite user" email template can greet the invited professional with
    the name of the hospital that invited them.
    """
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SupabaseAuthError("Supabase Auth invitation delivery is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    if not settings.invitation_frontend_route:
        raise SupabaseAuthError("Supabase Auth invitation redirect is not configured. Set INVITATION_FRONTEND_ROUTE.")

    # Generate the temporary password before calling Supabase so it can be
    # passed as custom template data - if the "Invite user" email template
    # (Supabase Dashboard > Authentication > Email Templates) has been
    # updated to reference {{ .Data.default_password }}, Supabase will send
    # it directly to the invited professional. It is also returned in this
    # function's result either way, so the inviting admin can share it
    # manually if the template hasn't been customized.
    temporary_password = generate_temporary_password()
    try:
        response = httpx.post(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/invite",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "Content-Type": "application/json",
            },
            json={
                "email": email,
                "redirect_to": settings.invitation_frontend_route,
                "data": {
                    "default_password": temporary_password,
                    "hospital_name": hospital_name or "your hospital",
                },
            },
            timeout=settings.default_timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAuthError("Supabase Auth invitation service is unavailable") from exc
    if response.is_error:
        try:
            detail: Any = response.json() if response.content else None
        except ValueError:
            detail = None
        message = None
        if isinstance(detail, dict):
            message = (
                detail.get("msg")
                or detail.get("message")
                or detail.get("error_description")
                or detail.get("error")
            )
        raise SupabaseAuthError(
            f"Supabase Auth rejected the invitation "
            f"(HTTP {response.status_code}): {message or detail or response.text or 'no response body'}"
        )
    try:
        user_id = response.json().get("id")
    except (ValueError, TypeError) as exc:
        raise SupabaseAuthError("Supabase Auth returned an invalid invitation response") from exc
    if not user_id:
        raise SupabaseAuthError("Supabase Auth did not return an invited user ID")
    set_user_password(str(user_id), temporary_password)
    return str(user_id), temporary_password