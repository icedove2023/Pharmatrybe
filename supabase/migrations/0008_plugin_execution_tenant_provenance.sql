alter table public.plugin_execution_audits
    add column if not exists authenticated_user_id uuid,
    add column if not exists professional_id uuid;
