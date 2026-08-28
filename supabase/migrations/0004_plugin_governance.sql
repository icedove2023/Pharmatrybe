create table if not exists public.plugin_governance_records (
    id uuid primary key default gen_random_uuid(),
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    plugin_id text not null,
    plugin_name text not null,
    plugin_type text not null check (plugin_type in ('knowledge', 'prediction')),
    plugin_version text not null,
    plugin_origin text not null default 'external',
    owner text not null,
    publisher text not null,
    artifact_hash text,
    artifact_uri text,
    capabilities jsonb not null default '[]'::jsonb,
    configuration jsonb not null default '{}'::jsonb,
    validation_state text not null default 'PENDING' check (validation_state in ('PENDING', 'VALIDATING', 'VALIDATED', 'REJECTED')),
    approval_state text not null default 'PENDING' check (approval_state in ('PENDING', 'APPROVED', 'REJECTED', 'REVOKED')),
    trust_level text not null default 'UNTRUSTED' check (trust_level in ('UNTRUSTED', 'VERIFIED', 'TRUSTED')),
    status text not null default 'PENDING_APPROVAL' check (status in ('SUBMITTED', 'VALIDATING', 'VALIDATED', 'PENDING_APPROVAL', 'APPROVED', 'ACTIVE', 'DISABLED', 'REJECTED', 'REVOKED', 'QUARANTINED')),
    submitted_by_user_id uuid,
    approved_by_user_id uuid,
    validated_by_user_id uuid,
    rejected_by_user_id uuid,
    revoked_by_user_id uuid,
    quarantined_by_user_id uuid,
    approved_at timestamptz,
    validated_at timestamptz,
    rejected_at timestamptz,
    revoked_at timestamptz,
    quarantined_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (hospital_id, plugin_id)
);

create index if not exists idx_plugin_governance_hospital_status
    on public.plugin_governance_records(hospital_id, status);

create table if not exists public.plugin_governance_audit_events (
    id uuid primary key default gen_random_uuid(),
    plugin_record_id uuid not null references public.plugin_governance_records(id) on delete cascade,
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    actor_user_id uuid,
    action text not null,
    details jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_plugin_governance_audit_record
    on public.plugin_governance_audit_events(plugin_record_id, created_at);

alter table public.plugin_governance_records enable row level security;
alter table public.plugin_governance_audit_events enable row level security;

create policy plugin_governance_no_client_select on public.plugin_governance_records
    for select using (false);
create policy plugin_governance_no_client_insert on public.plugin_governance_records
    for insert with check (false);
create policy plugin_governance_no_client_update on public.plugin_governance_records
    for update using (false) with check (false);
create policy plugin_governance_no_client_delete on public.plugin_governance_records
    for delete using (false);

create policy plugin_governance_audit_no_client_select on public.plugin_governance_audit_events
    for select using (false);
create policy plugin_governance_audit_no_client_insert on public.plugin_governance_audit_events
    for insert with check (false);
create policy plugin_governance_audit_no_client_update on public.plugin_governance_audit_events
    for update using (false) with check (false);
create policy plugin_governance_audit_no_client_delete on public.plugin_governance_audit_events
    for delete using (false);