alter table public.plugin_governance_records
    add column if not exists artifact_size bigint,
    add column if not exists manifest_metadata jsonb not null default '{}'::jsonb,
    add column if not exists security_validation jsonb not null default '{}'::jsonb,
    add column if not exists activated_by_user_id uuid,
    add column if not exists activated_at timestamptz;

alter table public.plugin_governance_records
    drop constraint if exists uq_plugin_governance_hospital_plugin;
alter table public.plugin_governance_records
    drop constraint if exists plugin_governance_records_hospital_id_plugin_id_key;

alter table public.plugin_governance_records
    add constraint uq_plugin_governance_artifact unique (hospital_id, plugin_id, plugin_version, artifact_hash);