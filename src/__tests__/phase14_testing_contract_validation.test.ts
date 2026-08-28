import { buildCanonicalResponse, recommendationApi } from '../api/recommendationApi';
import { authApi } from '../api/authApi';

export async function runPhase14ValidationTests() {
  const results: { name: string; passed: boolean; details?: string }[] = [];
  const assert = (condition: boolean, name: string, details?: string) => results.push({ name, passed: condition, details: condition ? undefined : details });
  const response = buildCanonicalResponse('PAT-1401', { age: 60, condition: 'Pneumonia' }, { Amoxicillin: 0.92 });
  assert(Object.keys(response).length === 11, 'Phase 14: canonical response field count is 11');
  assert(response.status === 'success' && response.confidence === 'high', 'Phase 14: canonical status and confidence are valid');
  assert(response.explanation !== undefined, 'Phase 14: explanation is represented as nullable contract data');
  assert(Array.isArray(response.evidence_attribution), 'Phase 14: empty attribution is valid');
  assert(!Object.keys(recommendationApi).some((key) => ['accept', 'override', 'modify', 'sign', 'prescription'].includes(key)), 'Phase 14: forbidden mutation methods are absent');
  assert(typeof authApi.login === 'function', 'Phase 14: authentication uses the approved provider-backed adapter');
  return results;
}
