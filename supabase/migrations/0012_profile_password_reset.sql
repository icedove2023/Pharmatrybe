-- Adds self-service profile fields (date of birth, forced password reset flag)
-- used by the Settings and Profile screens, and by the invited-user
-- default-password login flow.

alter table public.professional_profiles
  add column if not exists date_of_birth date,
  add column if not exists force_password_reset boolean not null default false;

comment on column public.professional_profiles.date_of_birth is
  'Optional self-reported date of birth; the Profile screen computes and displays age from this rather than storing a raw age value.';
comment on column public.professional_profiles.force_password_reset is
  'True for accounts provisioned with a temporary default password (e.g. hospital invitations). Cleared once the user sets their own password via Settings.';
