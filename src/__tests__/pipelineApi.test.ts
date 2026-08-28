import { pipelineApi } from '@/api/pipelineApi';

export function runPipelineApiTests() {
  const results: { name: string; passed: boolean; details?: string }[] = [];

  try {
    results.push({ name: 'pipelineApi exports executePipeline', passed: typeof pipelineApi.executePipeline === 'function' });
    results.push({ name: 'pipelineApi exports getExecutionStatus', passed: typeof pipelineApi.getExecutionStatus === 'function' });
    results.push({ name: 'pipelineApi exports generateRecommendationWithPredictions', passed: typeof pipelineApi.generateRecommendationWithPredictions === 'function' });
  } catch (e) {
    results.push({ name: 'pipelineApi basic probe', passed: false, details: (e as Error).message });
  }

  return results;
}
