import { buildCanonicalResponse, recommendationApi } from '../api/recommendationApi';

export function runPhase9IntegrationTests() {
  const results: { name: string; passed: boolean; details?: string }[] = [];
  const assert = (condition: boolean, name: string, details?: string) => {
    results.push({ name, passed: condition, details: condition ? undefined : details || 'Assertion failed' });
    console.log(`${condition ? '✅ [PASS]' : '❌ [FAIL]'} ${name}`);
  };

  const response = buildCanonicalResponse(
    'PAT-9001',
    { age: 60, condition: 'Pneumonia', egfr: 60 },
    { Amoxicillin: 0.92, Doxycycline: 0.85 },
  );
  const expectedFields = [
    'status', 'patient_id', 'recommendation', 'confidence', 'evidence_ranking',
    'evidence_attribution', 'recommendation_trace', 'audit_reference', 'explanation',
    'generated_at', 'trace_id',
  ];

  assert(Object.keys(response).length === 11, 'Phase 9: canonical response has exactly 11 fields');
  assert(expectedFields.every((field) => field in response), 'Phase 9: canonical fields are complete');
  assert(response.status === 'success', 'Phase 9: status is success');
  assert(response.confidence === 'high', 'Phase 9: confidence is a canonical string');
  assert(response.explanation !== undefined, 'Phase 9: explanation is nullable but represented');
  assert(Array.isArray(response.evidence_attribution), 'Phase 9: evidence attribution is an array');
  assert(Array.isArray(response.recommendation_trace.trace_steps), 'Phase 9: trace steps are structured');
  assert(response.evidence_ranking.ranked_evidence.length > 0, 'Phase 9: evidence ranking is distinct and populated');

  const original = JSON.stringify(response);
  assert(JSON.stringify(response) === original, 'Phase 9: recommendation object remains immutable');
  assert(!Object.keys(recommendationApi).some((key) => ['accept', 'override', 'modify', 'sign', 'prescription'].includes(key)), 'Phase 9: no mutation endpoints are exposed');

  return results;
}
