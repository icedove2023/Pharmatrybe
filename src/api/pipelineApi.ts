import { apiRequest } from './client';
import {
  ExplainabilityResponseContract,
} from '@/types';

export type ExecutionMode = 'sync' | 'async';
export type ResponseMode = 'full' | 'summary';

export interface PluginSelection {
  plugin_id: string;
  plugin_version?: string | null;
  plugin_role?: 'prediction' | 'knowledge' | string;
  configuration?: Record<string, any> | null;
}

export interface PipelineExecutionRequest {
  execution_mode?: ExecutionMode;
  patient_id?: string;
  case_id?: string | null;
  plugin_selection?: PluginSelection[];
  input_payload?: Record<string, any> | null;
  timeout_seconds?: number;
  response_mode?: ResponseMode;
}

export interface PipelineAccepted {
  status: 'accepted';
  execution_id: string;
  location?: string;
  message?: string;
}

export interface PipelineExecutionResult extends ExplainabilityResponseContract {
  // Extends the canonical explainability contract returned by recommendations
}

/**
 * Execute the server-orchestrated clinical decision pipeline.
 * - Returns a full ExplainabilityResponseContract when executed synchronously.
 * - Returns an accepted envelope when the server schedules async work.
 */
export async function executePipeline(request: PipelineExecutionRequest): Promise<PipelineExecutionResult | PipelineAccepted> {
  const resp = await apiRequest<any>('/pipeline/execute', {
    method: 'POST',
    body: JSON.stringify(request),
  });
  return resp as PipelineExecutionResult | PipelineAccepted;
}

/**
 * Poll / retrieve an async execution result or the execution status
 */
export async function getExecutionStatus(executionId: string): Promise<PipelineExecutionResult | { status: string; progress?: any }> {
  return apiRequest<any>(`/pipeline/executions/${executionId}`);
}

/**
 * Helper to request immediate generation via legacy recommendations endpoint when client supplies predictions.
 * Kept small here — callers should use recommendationApi where available.
 */
export async function generateRecommendationWithPredictions(payload: Record<string, any>): Promise<PipelineExecutionResult> {
  return apiRequest<PipelineExecutionResult>('/recommendations/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// Export a consolidated client object for convenience
export const pipelineApi = {
  executePipeline,
  getExecutionStatus,
  generateRecommendationWithPredictions,
};
