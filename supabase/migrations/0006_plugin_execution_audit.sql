create table if not exists public.plugin_execution_audits (
    id uuid primary key default gen_random_uuid(),
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    plugin_id text not null,
    plugin_version text,
    artifact_hash text,
    governance_record_id uuid references public.plugin_governance_records(id) on delete set null,
    execution_mode text not null,
    isolation_mode text not null,
    trust_level text,
    requested_capabilities jsonb not null default '[]'::jsonb,
    decision text not null check (decision in ('ALLOW', 'DENY')),
    execution_status text not null check (execution_status in ('SUCCESS', 'FAILURE')),
    started_at timestamptz not null,
    completed_at timestamptz not null,
    duration_ms double precision not null,
    timed_out boolean not null default false,
    denial_reason text,
    failure_reason text,
    isolation_level text,
    cpu_enforced boolean not null default false,
    memory_enforced boolean not null default false,
    network_enforced boolean not null default false,
    filesystem_enforced boolean not null default false,
    identity_enforced boolean not null default false,
    resource_policy_status text
);

create index if not exists idx_plugin_execution_audit_hospital_started
    on public.plugin_execution_audits(hospital_id, started_at);

alter table public.plugin_execution_audits enable row level security;
create policy plugin_execution_audit_no_client_select on public.plugin_execution_audits
    for select using (false);
create policy plugin_execution_audit_no_client_insert on public.plugin_execution_audits
    for insert with check (false);
create policy plugin_execution_audit_no_client_update on public.plugin_execution_audits
    for update using (false) with check (false);
create policy plugin_execution_audit_no_client_delete on public.plugin_execution_audits
    for delete using (false);
