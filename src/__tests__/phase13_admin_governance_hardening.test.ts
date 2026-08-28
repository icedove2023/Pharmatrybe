import { adminApi } from '../api/adminApi';
import { soarApi } from '../api/soarApi';
import { armdApi } from '../api/armdApi';

export async function runPhase13HardeningTests() {
  const results: { name: string; passed: boolean; details?: string }[] = [];
  const assert = (condition: boolean, name: string, details?: string) => results.push({ name, passed: condition, details: condition ? undefined : details });
  for (const [name, operation] of [
    ['Phase 13: SOAR surveillance is unavailable', () => soarApi.getSoarData()],
    ['Phase 13: ARMD models are unavailable', () => armdApi.getArmdModels()],
    ['Phase 13: audit log is unavailable', () => adminApi.getAuditEvents()],
  ] as const) {
    try {
      await operation();
      assert(false, name);
    } catch (error) {
      assert(error instanceof Error && error.message.includes('not exposed'), name, error instanceof Error ? error.message : String(error));
    }
  }
  return results;
}
