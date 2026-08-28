alter table public.plugin_execution_audits
    add column if not exists isolation_level text,
    add column if not exists cpu_enforced boolean not null default false,
    add column if not exists memory_enforced boolean not null default false,
    add column if not exists network_enforced boolean not null default false,
    add column if not exists filesystem_enforced boolean not null default false,
    add column if not exists identity_enforced boolean not null default false,
    add column if not exists resource_policy_status text;