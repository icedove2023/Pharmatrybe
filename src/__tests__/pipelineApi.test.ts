import { pipelineApi } from '@/api/pipelineApi';

export function runPipelineApiTests() {
  const results: { name: string; passed: boolean; details?: string }[] = [];

  try {
    results.push({ name: 'pipelineApi exports executePipeline', passed: typeof pipelineApi.executePipeline === 'function' });
  } catch (e) {
    results.push({ name: 'pipelineApi basic probe', passed: false, details: (e as Error).message });
  }

  return results;
}
