import type { ExplainabilityResponseContract } from '@/types';

export interface RoutingContext {
  deployment_id?: string;
}

export interface ApiFailurePayload {
  success: false;
  metadata: {
    request_id: string;
    timestamp: string;
    api_version: string;
    processing_time_ms: number;
  };
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown> | null;
  };
}

export interface CanonicalPipelineRequest {
  request_id?: string;
  patient_id: string;
  case_id?: string | null;
  input_payload: Record<string, unknown>;
  routing_context?: RoutingContext;
  plugin_selection?: Array<{
    plugin_id: string;
    plugin_version?: string | null;
    plugin_role?: string | null;
    configuration?: Record<string, unknown> | null;
  }>;
  execution_mode: 'sync';
  response_mode?: 'full' | 'summary';
}

export type CanonicalPipelineResponse = ExplainabilityResponseContract;
