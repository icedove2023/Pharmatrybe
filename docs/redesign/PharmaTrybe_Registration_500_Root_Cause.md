# PharmaTrybe — Update: Real Root Cause Found (Registration 500 Error)

This supersedes the earlier "backend not running" and "JWT signing key" theories — those were real, and fixing them got you further (the backend is now reachable and Supabase auth calls all return 200), but there's one more bug underneath, and this one **is** in your code, not your Supabase configuration.

## The exact error

```
Hospital registration failed: Foreign key associated with column
'professional_profiles.auth_user_id' could not find table 'auth.u[sers]'
```

## Why this happens

In `apps/api/app/models/identity.py`, `ProfessionalProfile.auth_user_id` is declared as:

```python
auth_user_id: Mapped[str] = mapped_column(
    Uuid(as_uuid=False),
    ForeignKey("auth.users.id", ondelete="CASCADE"),
    nullable=False,
    unique=True,
)
```

This is correct **at the raw SQL level** — your migration (`0001_identity_tenant_rls.sql`) already creates this constraint successfully against the real Postgres `auth.users` table that Supabase manages.

The problem is one level up, in **SQLAlchemy's Python object graph**. SQLAlchemy doesn't just trust the string `"auth.users.id"` — the first time it needs to build the mapper for `ProfessionalProfile` (which happens on your very first insert), it tries to resolve that string into an actual `Table` object registered on `Base.metadata`. Your codebase never defines a Python class/table for `auth.users` anywhere (there's no reason it would — Supabase owns that table, not your app). So SQLAlchemy searches its own registry, finds nothing called `auth.users`, and raises `NoReferencedTableError`, which the `except Exception` block in `register_hospital()` catches and reports as a generic 500.

This is a very common gotcha when combining Supabase (which owns `auth.users`) with a separate SQLAlchemy app schema — SQLAlchemy needs to know that table exists even if it doesn't manage it.

## The fix

Register a minimal, **unmanaged** stub for `auth.users` in the same `Base.metadata`, so SQLAlchemy can resolve the foreign key without SQLAlchemy ever trying to create/alter that table itself (Supabase already owns it).

In `apps/api/app/models/identity.py`, add this near the top, before `ProfessionalProfile`:

```python
class AuthUser(Base):
    """Read-only stub for Supabase's auth.users table.

    Not managed by our migrations — Supabase Auth owns this table. This
    class exists purely so SQLAlchemy can resolve the auth.users foreign
    key used by ProfessionalProfile.auth_user_id at mapper-configuration
    time; we never create, alter, or query through this model directly.
    """

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
```

No other changes are needed — `ForeignKey("auth.users.id", ...)` on `ProfessionalProfile` will now resolve correctly against this stub.

### Why this won't try to re-create or touch the real `auth.users` table
- This app doesn't appear to run `Base.metadata.create_all()` against the live database anywhere (schema changes go through the `supabase/migrations/*.sql` files instead) — so adding this class doesn't risk SQLAlchemy trying to `CREATE TABLE auth.users`.
- If you ever *do* introduce `Base.metadata.create_all()` (e.g. in a test fixture), pass `tables=[...]` explicitly listing only your own app tables, or exclude this stub, so it's never included.

## After applying the fix

1. Restart your backend (`uvicorn ...`).
2. Delete any orphaned Supabase Auth users from earlier failed attempts (Dashboard → Authentication → Users) that don't have a matching `professional_profiles` row.
3. Register a fresh hospital admin end-to-end — you should get a clean 200/201 from `register-hospital`, and see new rows appear in **Table Editor** under `hospitals`, `professional_profiles`, and `hospital_memberships`.
4. Once that works, login and the professional-invitation pipeline (which depends on this same identity chain) should also work.
