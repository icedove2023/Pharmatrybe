import { whoApi } from '../api/whoApi';
import { soarApi } from '../api/soarApi';
import { armdApi } from '../api/armdApi';
import { clinicalCasesApi } from '../api/clinicalCasesApi';
import { recommendationApi } from '../api/recommendationApi';

export interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
}

export async function runPhase10ExplorerTests(): Promise<TestResult[]> {
  const results: TestResult[] = [];
  const assert = (name: string, condition: boolean, error?: string) => {
    results.push({ name, passed: condition, error: condition ? undefined : error || 'Assertion failed' });
  };
  const expectUnavailable = async (name: string, operation: Promise<unknown>) => {
    try {
      await operation;
      assert(name, false, 'Unavailable backend capability returned data');
    } catch (error) {
      assert(name, error instanceof Error && error.message.includes('not exposed'), error instanceof Error ? error.message : String(error));
    }
  };

  for (const method of [
    'getWhoDiseases', 'getWhoDiseaseById', 'searchWhoDiseases', 'getWhoRecommendations',
    'getWhoEvidence', 'getWhoGuideline', 'getWhoPathogens', 'getWhoStewardship',
    'getWhoMonitoring', 'getWhoDiagnostics', 'getWhoFollowUp', 'getWhoReferral',
  ]) {
    assert(`WHO API exposes ${method}`, typeof whoApi[method as keyof typeof whoApi] === 'function');
  }
  assert('Clinical case API exposes list/detail/create methods', typeof clinicalCasesApi.getClinicalCases === 'function' && typeof clinicalCasesApi.getClinicalCaseById === 'function' && typeof clinicalCasesApi.submitClinicalCase === 'function');
  assert('Canonical recommendation method is exposed', typeof recommendationApi.generateRecommendation === 'function');

  await expectUnavailable('SOAR surveillance records are explicitly unavailable', soarApi.getSoarData());
  await expectUnavailable('ARMD model registry is explicitly unavailable', armdApi.getArmdModels());

  return results;
}
