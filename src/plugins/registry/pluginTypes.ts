/**
 * Phase 11: Plugin Registry & Model Telemetry Types
 * Strongly typed contracts for the frontend Plugin Registry, Provenance, and Telemetry models.
 */

export type PluginStatus =
  | 'available'
  | 'unavailable'
  | 'degraded'
  | 'unknown';

export type PluginCategory =
  | 'knowledge'
  | 'prediction'
  | 'rules'
  | 'fusion'
  | 'explainability'
  | 'audit'
  | 'risk'
  | 'reporting'
  | 'integration';

export type PluginFormFieldType = 'text' | 'number' | 'select' | 'checkbox' | 'textarea';

export interface PluginFormField {
  id: string;
  label: string;
  type: PluginFormFieldType;
  path: string;
  required?: boolean;
  placeholder?: string;
  helpText?: string;
  step?: string;
  options?: Array<{ label: string; value: string }>;
}

export interface PluginDefinition {
  id: string;
  backendId?: string;
  name: string;
  category: PluginCategory;
  description: string;
  role: string;
  status: PluginStatus;
  version?: string;
  modelVersion?: string;
  source?: string;
  capabilities: string[];
  isCore?: boolean;
  metadata?: Record<string, any>;
  formSchema?: PluginFormField[];
}

export type PluginContributionType =
  | 'prediction'
  | 'evidence'
  | 'rule'
  | 'fusion'
  | 'explanation'
  | 'unknown';

export interface PluginContribution {
  pluginId: string;
  pluginName?: string;
  category?: PluginCategory;
  contributionType: PluginContributionType;
  source?: string;
  modelVersion?: string;
  weight?: number;
  attribution?: unknown;
  details?: string;
  timestamp?: string;
}

export interface RecommendationTelemetry {
  traceId?: string;
  generatedAt?: string;
  auditReference?: Record<string, unknown>;
  confidence?: string;
  recommendationId?: string;
  pluginContributions?: PluginContribution[];
  predictionPluginVersion?: string;
  modelVersions?: Record<string, string>;
  ruleVersions?: string;
  guidelineEngineVersion?: string;
  stewardshipEngineVersion?: string;
  cdssVersion?: string;
  algorithmVersion?: string;
  totalDurationMs?: number;
  traceStepsCount?: number;
}
