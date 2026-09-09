# PharmaTrybe — Supabase Email Templates Setup

Three ready-to-use HTML templates are included in `docs/email-templates/`:

| File | Supabase template slot | Greets with |
|---|---|---|
| `confirm_signup.html` | Authentication → Email Templates → **Confirm signup** | `Dear {{ .Data.first_name }}` |
| `invite_user.html` | Authentication → Email Templates → **Invite user** | Hospital name that invited them |
| `reset_password.html` | Authentication → Email Templates → **Reset password** | `Dear {{ .Data.first_name }}` |

## How to install each one

1. Open **Supabase Dashboard → your project → Authentication → Email Templates**.
2. Click the template name (e.g. "Confirm signup").
3. Open the corresponding `.html` file from `docs/email-templates/` in this zip, copy its contents (the comment block at the top is just documentation — safe to leave in or strip out, Supabase ignores HTML comments), and paste into the **Message body (HTML)** field, replacing what's there.
4. Click **Save**.
5. Repeat for the other two templates.

## Why each variable is guaranteed to work

- **`{{ .Data.first_name }}` (Confirm signup)** — set explicitly in `src/api/authApi.ts`'s `registerHospital()`, passed to `supabase.auth.signUp({ options: { data: { first_name: ... } } })`. Always present for hospital admin signups.
- **`{{ .Data.hospital_name }}` and `{{ .Data.default_password }}` (Invite user)** — set explicitly in `apps/api/app/services/identity/supabase_auth.py`'s `invite_user_by_email()`, passed in the `data` field of the `POST /auth/v1/invite` call. Always present for invitations sent through the "Invite a professional" screen.
- **`{{ .Data.first_name }}` (Reset password)** — Supabase populates `.Data` from the target user's existing `user_metadata` for every template, not just the one that originally set it. Since hospital admins have `first_name` saved at signup, it carries through automatically to their reset-password email. Invited professionals who haven't yet set their name (via Settings) will see the "there" fallback instead — this is expected and not an error.

## What still needs a person, not code

Editing these templates has to happen in the Supabase Dashboard — Supabase doesn't expose an API to update email templates programmatically, so this step can't be automated from the codebase. Everything on the *data* side (passing `first_name`, `hospital_name`, `default_password` into each email) is already wired up in the code included in this zip; only the *template HTML* itself needs to be pasted in manually, once, per project.

## Related: enforcing email verification before registration completes

As part of this update, hospital registration now has a **backend-enforced** email-verification gate (`apps/api/app/api/v1/auth.py::register_hospital`, using the new `is_email_confirmed()` helper in `supabase_auth.py`). Even if Supabase's "Confirm email" dashboard toggle is ever left off, `POST /auth/register-hospital` will refuse to create the hospital until the account's email is actually confirmed, returning a clear `EMAIL_NOT_VERIFIED` error. The frontend (`authApi.ts`) already handles this: it keeps the pending registration data intact and shows "Please check your Gmail inbox and confirm your email address, then sign in to finish setting up your hospital," so registration completes automatically on their next sign-in after confirming.

**One dashboard setting is still required for this to actually prompt a confirmation email in the first place:** go to **Authentication → Sign In / Providers → Email** and make sure **"Confirm email"** is turned ON. Without it, Supabase auto-confirms every signup immediately (no email sent, and the backend check above will simply always pass), so registration would complete right away without ever requiring the Gmail step you asked for.
