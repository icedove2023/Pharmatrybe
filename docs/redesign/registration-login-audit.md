# PharmaTrybe — Registration & Login Pipeline Audit

**Symptom reported:** Registering creates a user in Supabase Auth, but "registration"
fails; a subsequent login attempt then shows an error.

**Root cause (confirmed in code):** registration is split into two separate steps that
are only *loosely* stitched together on the client, using `localStorage` as the glue.
When that glue doesn't hold — which is the default behavior for a new Supabase
project — the Supabase Auth user exists, but the corresponding hospital/professional
record in your own database is never created, so every later request (including
login) fails with **403 `ACCOUNT_INACTIVE`**.

---

## 1. How registration is currently wired

`src/api/authApi.ts`:

```ts
registerHospital: async (payload) => {
  savePendingRegistration(payload);           // 1. stash form data in localStorage
  const { data, error } = await supabase.auth.signUp({ ... });   // 2. create Supabase Auth user
  if (error) throw new AuthError(error.message);
  if (!data.session) return null;              // 3. <-- if no session, STOP HERE
  await completePendingRegistration(...);       // 4. only runs if a session came back
  ...
}
```

Step 4 (`POST /auth/register-hospital`, which creates the `Hospital`,
`ProfessionalProfile`, `HospitalMembership` and role rows in your database) **only
runs if `supabase.auth.signUp()` returns a session immediately.**

`supabase.auth.signUp()` only returns a session immediately when **"Confirm email"
is turned off** in Supabase. That is not the default: a stock Supabase project ships
with **email confirmation required**, in which case `signUp()` returns a user but
`data.session` is `null`. Your `HospitalRegistrationForm.tsx` even has UI for this
exact case ("Check your email… then return here and sign in to finish creating your
hospital workspace"), so the app was built expecting this path to be the common one.

So on a normal signup:
- ✅ A row is created in Supabase's `auth.users` table → "it creates an account on
  Supabase."
- ❌ `register-hospital` is never called → no `Hospital`/`ProfessionalProfile` row
  exists → "registration fails" (the workspace is never actually created).

## 2. Why login then also fails

The only remaining place that tries to finish the job is a `localStorage` value
called `pharmatrybe.pending-hospital-registration`, written in step 1 above. It's
read back in `login()` and `getCurrentSession()`:

```ts
async function completePendingRegistration(email: string) {
  const raw = window.localStorage.getItem(PENDING_HOSPITAL_REGISTRATION);
  if (!raw) return false;                 // nothing to do → silently skipped
  ...
  await apiRequest('/auth/register-hospital', { ... });
  window.localStorage.removeItem(PENDING_HOSPITAL_REGISTRATION);
  return true;
}
```

This only succeeds if the person logs in **on the same browser, same device, without
having cleared site data**, after registering. It silently does nothing otherwise —
there is no error, no retry, and no indicator that the workspace was never created.

Once that step is skipped, `login()` proceeds to call `getApplicationUser()` →
`GET /auth/me`. On the backend, `get_authorization_context()`
(`apps/api/app/auth/dependencies.py`) looks up a `ProfessionalProfile` for the
Supabase user ID:

```python
if professional is None or professional.profile_status != "ACTIVE":
    raise HTTPException(403, detail={"code": "ACCOUNT_INACTIVE", ...})
```

Because no such profile was ever created, this **always** raises `403
ACCOUNT_INACTIVE` — which is the login error you're seeing. Supabase Auth itself is
happy (the password is correct); it's your application-level record that's missing.

### This can also happen even when it "works"
Even when the confirmation email is clicked on the *same* device, there's a second
failure mode: clicking the Supabase confirmation link auto-creates a session and
fires a `SIGNED_IN` event (`detectSessionInUrl: true`). `authStore.ts`'s listener
reacts to that event by calling `getCurrentSession()`, which also tries to run
`completePendingRegistration()` — **at the same time** the user may separately submit
the login form, which calls `authApi.login()`, which does the same thing again. Two
concurrent calls to `POST /auth/register-hospital` can both pass the "does a profile
already exist?" check before either commits, and the loser then hits a database
uniqueness conflict and gets converted into a generic `500`
`"Hospital registration failed"`. This is intermittent and will look like "login just
randomly errors sometimes."

## 3. Is this a Supabase configuration problem, or a code problem?

**It's primarily a code/architecture problem**, not a Supabase misconfiguration:
Supabase is behaving exactly as configured (email confirmation on by default).
The application was written assuming that behavior, but the mechanism it uses to
resume registration after confirmation (`localStorage`) is fragile and has no
error handling or retry path.

Two things are still worth checking on the Supabase side while you're in there,
because they affect how reliably confirmation links work:

- **Auth → Providers → Email → "Confirm email"**: know whether this is on or off for
  your project; the fix below needs to work correctly either way.
- **Auth → URL Configuration → Redirect URLs**: the confirmation link redirects the
  user back into your app. Confirm your local/deployed app URL(s) are on that
  allow list — Supabase will reject the redirect otherwise, which can also present
  as "the account exists but nothing happens after registering."

## 4. Recommended fix

Move the "create hospital + admin profile" step so it **no longer depends on
`localStorage` or which device confirms the email.** The cleanest fix is to make
account creation transactional from the user's point of view:

1. **Preferred:** Call `signUp()` and immediately call `/auth/register-hospital`
   using a short‑lived signal from Supabase (the `data.user.id` is available even
   without a session) — have the backend accept the request authenticated by the
   just-created `user.id` via a signed one-time server-to-server call, **or**
   simpler: turn **off "Confirm email"** for this flow and instead verify the hospital
   admin's email via your own follow-up step, so `signUp()` always returns a session
   and `register-hospital` can run synchronously in `registerHospital()` before
   returning.
2. **If you keep email confirmation on:** don't rely on `localStorage`. Instead,
   store the pending hospital payload **server-side**, keyed by the Supabase
   `user.id` returned from `signUp()` (e.g. a `pending_hospital_registrations`
   table), and have `/auth/me` (or a dedicated endpoint) auto-create the hospital
   the first time that now-confirmed user authenticates — regardless of which
   browser/device they used to click the link. This removes the client-side race
   entirely.
3. **Make `/auth/register-hospital` idempotent and safe to call twice**: catch the
   "profile already exists" case (already partially done) and return the existing
   membership instead of erroring, so the double-invocation race in §2 becomes a
   harmless no-op instead of a `500`.
4. **Surface failures instead of swallowing them.** Today, if
   `completePendingRegistration()` fails inside `getCurrentSession()`, the whole
   session is treated as invalid and the user is silently signed out
   (`clearApplicationSession('session-invalid')`). Show them an actionable message
   ("We verified your email but couldn't finish setting up your hospital — please
   contact support / retry") instead.
5. Add basic **observability**: log/alert when a Supabase Auth user is created but
   no `ProfessionalProfile` exists after some time window (e.g. 24h), so orphaned
   accounts like this are caught proactively rather than reported by users.

## 5. Is the registration form itself sufficient?

No — comparing the form to your own database schema shows several fields your
backend already supports but the form never collects:

| Field | In schema? | Collected at registration? |
|---|---|---|
| Hospital legal name (`hospitals.legal_name`) | ✅ | ❌ defaults to hospital name |
| Hospital code (`hospitals.hospital_code`) | ✅ | ❌ |
| Admin phone (`professional_profiles.phone`) | ✅ | ❌ |
| Admin professional registration/license number (`professional_profiles.professional_registration_number`) | ✅ | ❌ |
| Hospital address | ❌ (no column at all) | ❌ |

Recommendations:
- Add **phone number** and **professional registration/license number** fields to
  `HospitalRegistrationForm.tsx` and pass them through to
  `POST /auth/register-hospital` — the backend model already has columns for both,
  they're just never populated.
- Consider whether `legal_name` and a hospital `address` are required for your
  compliance/reporting needs; if so, add the fields (and a migration for `address`,
  since no column currently exists) and collect them at registration rather than
  leaving them to be edited later.
- Add a **duplicate-hospital / duplicate-admin-email check with a clear message**
  before calling Supabase, so a re-attempted registration doesn't just look like a
  silent failure.
