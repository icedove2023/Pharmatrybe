create table if not exists public.invitation_delivery_outbox (
    id uuid primary key default gen_random_uuid(),
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    invitation_id uuid not null unique references public.hospital_invitations(id) on delete cascade,
    idempotency_key text not null unique,
    delivery_type text not null,
    recipient_email text not null,
    payload jsonb not null,
    status text not null default 'PENDING' check (status in ('PENDING', 'PROCESSING', 'SENT', 'FAILED')),
    attempt_count integer not null default 0 check (attempt_count >= 0 and attempt_count <= 3),
    available_at timestamptz not null,
    processing_started_at timestamptz,
    last_attempt_at timestamptz,
    last_error_code text,
    last_error_message text,
    completed_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_invitation_outbox_pending_available
    on public.invitation_delivery_outbox(status, available_at);
create index if not exists idx_invitation_outbox_processing_started
    on public.invitation_delivery_outbox(status, processing_started_at);
create index if not exists idx_invitation_outbox_invitation
    on public.invitation_delivery_outbox(invitation_id);

alter table public.invitation_delivery_outbox enable row level security;

create policy invitation_outbox_no_client_select on public.invitation_delivery_outbox
    for select using (false);
create policy invitation_outbox_no_client_insert on public.invitation_delivery_outbox
    for insert with check (false);
create policy invitation_outbox_no_client_update on public.invitation_delivery_outbox
    for update using (false) with check (false);
create policy invitation_outbox_no_client_delete on public.invitation_delivery_outbox
    for delete using (false);

create table if not exists public.invitation_token_handoffs (
    reference text primary key,
    invitation_id uuid not null references public.hospital_invitations(id) on delete cascade,
    hospital_id uuid not null references public.hospitals(id) on delete cascade,
    outbox_id uuid not null unique references public.invitation_delivery_outbox(id) on delete cascade,
    encrypted_token text not null,
    expires_at timestamptz not null,
    created_at timestamptz not null default now()
);

alter table public.invitation_token_handoffs enable row level security;

create policy invitation_handoffs_no_client_select on public.invitation_token_handoffs
    for select using (false);
create policy invitation_handoffs_no_client_insert on public.invitation_token_handoffs
    for insert with check (false);
create policy invitation_handoffs_no_client_update on public.invitation_token_handoffs
    for update using (false) with check (false);
create policy invitation_handoffs_no_client_delete on public.invitation_token_handoffs
    for delete using (false);