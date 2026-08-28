-- Phase 16C canonical RBAC seed.
-- Only unconditional check-mark grants become role_permissions rows.
-- Policy, Limited, Approved, and Controlled cells remain contextual and are
-- intentionally not represented as static grants in this migration.

insert into public.roles (code, name, description) values
    ('HOSPITAL_ADMIN', 'Hospital Administrator', 'Hospital administration and governance'),
    ('CLINICIAN', 'Clinician', 'Clinical assessment and recommendation workflow'),
    ('PHARMACIST', 'Pharmacist', 'Medication review and stewardship'),
    ('LABORATORY_SCIENTIST', 'Laboratory Scientist', 'Laboratory diagnostics and AST'),
    ('INFECTIOUS_DISEASE_SPECIALIST', 'Infectious Disease Specialist', 'Complex antimicrobial resistance case review'),
    ('RESEARCHER', 'Researcher', 'Approved read-only research access')
on conflict (code) do update set name = excluded.name, description = excluded.description;

insert into public.permissions (code, description) values
    ('hospital:view', 'View the hospital profile'),
    ('hospital:update', 'Update the hospital profile'),
    ('professionals:invite', 'Invite professionals to the hospital'),
    ('professionals:view', 'View hospital professionals'),
    ('professionals:manage', 'Manage professional memberships, including activation, suspension, and deactivation'),
    ('roles:assign', 'Assign canonical roles to memberships'),
    ('patients:view', 'View patient records subject to contextual policy'),
    ('patients:create', 'Create patient records subject to contextual policy'),
    ('cases:view', 'View clinical cases'),
    ('cases:create', 'Create clinical cases'),
    ('cases:update', 'Update clinical cases subject to resource policy'),
    ('laboratory:view', 'View laboratory results'),
    ('laboratory:create', 'Enter laboratory results'),
    ('recommendations:view', 'View recommendations subject to contextual policy'),
    ('recommendations:request', 'Request recommendations'),
    ('recommendations:review', 'Review recommendations subject to contextual policy'),
    ('guidelines:view', 'View global WHO and guideline knowledge'),
    ('guidelines:manage', 'Manage hospital guidelines'),
    ('stewardship:view', 'View stewardship policies'),
    ('stewardship:manage', 'Manage stewardship policies subject to contextual policy'),
    ('plugins:view', 'View configured plugins'),
    ('plugins:configure', 'Configure plugins'),
    ('workflows:manage', 'Manage workflows'),
    ('workflows:execute', 'Execute approved workflows subject to approval policy'),
    ('audit:view', 'View audit events subject to scope policy'),
    ('data:export', 'Export data subject to controlled policy')
on conflict (code) do update set description = excluded.description;

with grants(role_code, permission_code) as (
    values
        ('HOSPITAL_ADMIN', 'hospital:view'),
        ('HOSPITAL_ADMIN', 'hospital:update'),
        ('HOSPITAL_ADMIN', 'professionals:invite'),
        ('HOSPITAL_ADMIN', 'professionals:view'),
        ('HOSPITAL_ADMIN', 'professionals:manage'),
        ('HOSPITAL_ADMIN', 'roles:assign'),
        ('HOSPITAL_ADMIN', 'guidelines:view'),
        ('HOSPITAL_ADMIN', 'guidelines:manage'),
        ('HOSPITAL_ADMIN', 'stewardship:view'),
        ('HOSPITAL_ADMIN', 'plugins:view'),
        ('HOSPITAL_ADMIN', 'plugins:configure'),
        ('HOSPITAL_ADMIN', 'workflows:manage'),
        ('HOSPITAL_ADMIN', 'audit:view'),
        ('CLINICIAN', 'hospital:view'),
        ('CLINICIAN', 'professionals:view'),
        ('CLINICIAN', 'patients:view'),
        ('CLINICIAN', 'patients:create'),
        ('CLINICIAN', 'cases:view'),
        ('CLINICIAN', 'cases:create'),
        ('CLINICIAN', 'cases:update'),
        ('CLINICIAN', 'laboratory:view'),
        ('CLINICIAN', 'recommendations:view'),
        ('CLINICIAN', 'recommendations:request'),
        ('CLINICIAN', 'recommendations:review'),
        ('CLINICIAN', 'guidelines:view'),
        ('CLINICIAN', 'stewardship:view'),
        ('CLINICIAN', 'workflows:execute'),
        ('PHARMACIST', 'hospital:view'),
        ('PHARMACIST', 'professionals:view'),
        ('PHARMACIST', 'patients:view'),
        ('PHARMACIST', 'cases:view'),
        ('PHARMACIST', 'cases:create'),
        ('PHARMACIST', 'laboratory:view'),
        ('PHARMACIST', 'recommendations:view'),
        ('PHARMACIST', 'recommendations:request'),
        ('PHARMACIST', 'recommendations:review'),
        ('PHARMACIST', 'guidelines:view'),
        ('PHARMACIST', 'stewardship:view'),
        ('PHARMACIST', 'workflows:execute'),
        ('LABORATORY_SCIENTIST', 'hospital:view'),
        ('LABORATORY_SCIENTIST', 'professionals:view'),
        ('LABORATORY_SCIENTIST', 'cases:view'),
        ('LABORATORY_SCIENTIST', 'laboratory:view'),
        ('LABORATORY_SCIENTIST', 'laboratory:create'),
        ('LABORATORY_SCIENTIST', 'guidelines:view'),
        ('LABORATORY_SCIENTIST', 'stewardship:view'),
        ('LABORATORY_SCIENTIST', 'workflows:execute'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'hospital:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'professionals:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'patients:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'patients:create'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'cases:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'cases:create'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'cases:update'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'laboratory:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'recommendations:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'recommendations:request'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'recommendations:review'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'guidelines:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'stewardship:view'),
        ('INFECTIOUS_DISEASE_SPECIALIST', 'workflows:execute'),
        ('RESEARCHER', 'guidelines:view')
)
insert into public.role_permissions (role_id, permission_id)
select roles.id, permissions.id
from grants
join public.roles on roles.code = grants.role_code
join public.permissions on permissions.code = grants.permission_code
on conflict (role_id, permission_id) do nothing;