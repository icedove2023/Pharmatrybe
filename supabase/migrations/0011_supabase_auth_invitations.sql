alter table public.hospital_invitations
    alter column token_hash drop not null;

alter table public.hospital_invitations
    add column if not exists supabase_user_id uuid unique;

alter table public.hospital_invitations
    add constraint hospital_invitations_supabase_user_fk
    foreign key (supabase_user_id) references auth.users(id) on delete set null;