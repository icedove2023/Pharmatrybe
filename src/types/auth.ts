import { z } from 'zod';

export type UserRole =
  | 'Infectious Disease Specialist'
  | 'General Practitioner'
  | 'Pharmacist'
   | 'Laboratory Scientist'
  | 'Admin'
  | 'Researcher';

export type BackendRoleCode = string;
export type BackendPermissionCode = string;

export interface RolePermissions {
  canSubmitAssessment: boolean;
  canViewRecommendations: boolean;
  canSignPrescription: boolean;
  canOverrideStewardship: boolean;
  canViewExplainability: boolean;
  canAccessKnowledgeExplorer: boolean;
  canViewPatientDirectory: boolean;
  canManagePlugins: boolean;
  canViewSystemHealth: boolean;
  canManageUsers: boolean;
  canViewAuditLogs: boolean;
}

export interface User {
  id: string;
  professionalId?: string;
  membershipId?: string;
  hospitalId?: string;
  name: string;
  email: string;
  role: UserRole;
  organization: string;
  department: string;
  licenseNumber?: string;
  avatarUrl?: string;
  lastLogin?: string;
  permissions: RolePermissions;
  roles: BackendRoleCode[];
  permissionCodes: BackendPermissionCode[];
}

export interface AuthSession {
  expiresAt: string;
  traceSessionId: string;
}

export const loginSchema = z.object({
  email: z.string().min(1, 'Email address is required').email('Invalid email address format'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  rememberMe: z.boolean().optional(),
});

export type LoginCredentials = z.infer<typeof loginSchema>;

export interface HospitalOrganization {
  id: string;
  name: string;
  country: string;
  address?: string;
  createdAt: string;
}

const passwordRule = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must include an uppercase letter')
  .regex(/[0-9]/, 'Password must include a number');

export const hospitalRegistrationSchema = z
  .object({
    hospitalName: z.string().min(2, 'Hospital / institution name is required'),
    country: z.string().min(2, 'Country is required'),
    adminName: z.string().min(2, 'Full name is required'),
    adminEmail: z.string().min(1, 'Work email is required').email('Invalid email address'),
    adminPhone: z.string().min(5, 'Valid phone number required').optional(),
    adminProfessionalNumber: z.string().min(2, 'Professional registration/license number is required').optional(),
    password: passwordRule,
    confirmPassword: z.string(),
    acceptTerms: z.literal(true, { message: 'You must acknowledge the terms to continue' }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type HospitalRegistrationPayload = z.infer<typeof hospitalRegistrationSchema>;

export const createEmployeeSchema = z.object({
  name: z.string().min(2, 'Full name is required'),
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  role: z.enum([
    'Infectious Disease Specialist',
    'General Practitioner',
    'Pharmacist',
    'Admin',
    'Researcher',
  ]),
  department: z.string().min(1, 'Department is required'),
  licenseNumber: z.string().optional(),
});

export type CreateEmployeePayload = z.infer<typeof createEmployeeSchema>;

// Frontend presentation permission mappings
// NOTE: These permissions govern UI visibility and client-side navigation.
// Authoritative security and role authorization are strictly enforced server-side by the backend API.
export const ROLE_PERMISSIONS_MAP: Record<UserRole, RolePermissions> = {
  'Infectious Disease Specialist': {
    canSubmitAssessment: true,
    canViewRecommendations: true,
    canSignPrescription: true,
    canOverrideStewardship: true,
    canViewExplainability: true,
    canAccessKnowledgeExplorer: true,
    canViewPatientDirectory: true,
    canManagePlugins: false,
    canViewSystemHealth: false,
    canManageUsers: false,
    canViewAuditLogs: false,
  },
  'General Practitioner': {
    canSubmitAssessment: true,
    canViewRecommendations: true,
    canSignPrescription: true,
    canOverrideStewardship: false,
    canViewExplainability: true,
    canAccessKnowledgeExplorer: true,
    canViewPatientDirectory: true,
    canManagePlugins: false,
    canViewSystemHealth: false,
    canManageUsers: false,
    canViewAuditLogs: false,
  },
  'Pharmacist': {
    canSubmitAssessment: true,
    canViewRecommendations: true,
    canSignPrescription: false,
    canOverrideStewardship: true,
    canViewExplainability: true,
    canAccessKnowledgeExplorer: true,
    canViewPatientDirectory: true,
    canManagePlugins: false,
    canViewSystemHealth: false,
    canManageUsers: false,
    canViewAuditLogs: false,
  },
  'Admin': {
    canSubmitAssessment: true,
    canViewRecommendations: true,
    canSignPrescription: false,
    canOverrideStewardship: false,
    canViewExplainability: true,
    canAccessKnowledgeExplorer: true,
    canViewPatientDirectory: true,
    canManagePlugins: true,
    canViewSystemHealth: true,
    canManageUsers: true,
    canViewAuditLogs: true,
  },
  'Researcher': {
    canSubmitAssessment: false,
    canViewRecommendations: false,
    canSignPrescription: false,
    canOverrideStewardship: false,
    canViewExplainability: true,
    canAccessKnowledgeExplorer: true,
    canViewPatientDirectory: true, // De-identified
    canManagePlugins: false,
    canViewSystemHealth: true,
    canManageUsers: false,
    canViewAuditLogs: false,
  },
   'Laboratory Scientist': {
     canSubmitAssessment: false,
     canViewRecommendations: false,
     canSignPrescription: false,
     canOverrideStewardship: false,
     canViewExplainability: false,
     canAccessKnowledgeExplorer: true,
     canViewPatientDirectory: false,
     canManagePlugins: false,
     canViewSystemHealth: false,
     canManageUsers: false,
     canViewAuditLogs: false,
   },
};
