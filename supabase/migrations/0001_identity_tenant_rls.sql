-- Phase 6F identity and tenant foundation.
-- FastAPI remains the primary authorization authority; these policies are defense in depth.

create table if not exists public.hospitals (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    legal_name text,
    hospital_code text unique,
    status text not null default 'ACTIVE',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.professional_profiles (
    id uuid primary key default gen_random_uuid(),
    auth_user_id uuid not null unique references auth.users(id) on delete cascade,
    first_name text not null,
    last_name text not null,
    professional_type text,
    professional_registration_number text,
    phone text,
    profile_status text not null default 'ACTIVE',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.roles (
    id uuid primary key default gen_random_uuid(),
    code text not null unique,
    name text not null,
    description text
);

create table if not exists public.permissions (
    id uuid primary key default gen_random_uuid(),
    code text not null unique,
    description text
);

create table if not exists public.role_permissions (
    role_id uuid not null references public.roles(id) on delete cascade,
    permission_id uuid not null references public.permissions(id) on delete cascade,
    primary key (role_id, permission_id)
);

create table if not exists public.hospital_memberships (
    id uuid primary key default gen_random_uuid(),
    professional_id uuid not null references public.professional_profiles(id) on delete cascade,
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    status text not null default 'INVITED',
    invited_by uuid,
    joined_at timestamptz,
    activated_at timestamptz,
    suspended_at timestamptz,
    deactivated_at timestamptz,
    ended_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists idx_one_active_membership_per_professional
    on public.hospital_memberships (professional_id)
    where status = 'ACTIVE';

create table if not exists public.membership_roles (
    membership_id uuid not null references public.hospital_memberships(id) on delete cascade,
    role_id uuid not null references public.roles(id) on delete cascade,
    assigned_by uuid,
    assigned_at timestamptz not null default now(),
    primary key (membership_id, role_id)
);

create table if not exists public.hospital_invitations (
    id uuid primary key default gen_random_uuid(),
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    email text not null,
    invited_by uuid not null,
    role_code text not null,
    token_hash text not null unique,
    status text not null default 'PENDING',
    expires_at timestamptz not null,
    accepted_at timestamptz,
    created_at timestamptz not null default now()
);

create table if not exists public.membership_events (
    id uuid primary key default gen_random_uuid(),
    membership_id uuid not null references public.hospital_memberships(id) on delete cascade,
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    actor_user_id uuid not null,
    event_type text not null,
    details jsonb,
    created_at timestamptz not null default now()
);

create or replace function public.current_hospital_id()
returns uuid
language sql
stable
security definer
set search_path = public
as $$
    select hm.hospital_id
    from public.hospital_memberships hm
    join public.professional_profiles pp on pp.id = hm.professional_id
    where pp.auth_user_id = auth.uid()
      and hm.status = 'ACTIVE'
    limit 1
$$;

alter table public.hospitals enable row level security;
alter table public.professional_profiles enable row level security;
alter table public.roles enable row level security;
alter table public.permissions enable row level security;
alter table public.role_permissions enable row level security;
alter table public.hospital_memberships enable row level security;
alter table public.membership_roles enable row level security;
alter table public.hospital_invitations enable row level security;
alter table public.membership_events enable row level security;

create policy hospitals_member_read on public.hospitals
    for select using (id = public.current_hospital_id());

create policy profiles_self_read on public.professional_profiles
    for select using (auth_user_id = auth.uid());

create policy memberships_same_hospital_read on public.hospital_memberships
    for select using (hospital_id = public.current_hospital_id());

create policy membership_roles_same_hospital_read on public.membership_roles
    for select using (
        exists (
            select 1 from public.hospital_memberships hm
            where hm.id = membership_roles.membership_id
              and hm.hospital_id = public.current_hospital_id()
        )
    );

create policy roles_read_authenticated on public.roles
    for select using (auth.uid() is not null);

create policy permissions_read_authenticated on public.permissions
    for select using (auth.uid() is not null);

create policy role_permissions_read_authenticated on public.role_permissions
    for select using (auth.uid() is not null);

create policy invitations_same_hospital_read on public.hospital_invitations
    for select using (hospital_id = public.current_hospital_id());

create policy membership_events_same_hospital_read on public.membership_events
    for select using (hospital_id = public.current_hospital_id());