import { apiRequest } from './client';
import {
  ExplainabilityResponseContract,
} from '@/types';
import type { CanonicalPipelineRequest } from './types';

export type ExecutionMode = 'sync';
export type ResponseMode = 'full' | 'summary';

export type PipelineExecutionRequest = CanonicalPipelineRequest;

export interface PipelineExecutionResult extends ExplainabilityResponseContract {
  // Extends the canonical explainability contract returned by recommendations
}

/**
 * Execute the server-orchestrated clinical decision pipeline.
 * Returns the canonical synchronous explainability response.
 */
export async function executePipeline(request: PipelineExecutionRequest): Promise<PipelineExecutionResult> {
  return apiRequest<PipelineExecutionResult>('/pipeline/execute', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// Export a consolidated client object for convenience
export const pipelineApi = {
  executePipeline,
};
