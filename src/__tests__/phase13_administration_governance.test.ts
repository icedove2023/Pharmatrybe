import { adminApi } from '../api/adminApi';

export async function runPhase13AdminGovernanceTests() {
  const results: { name: string; passed: boolean; details?: string }[] = [];
  const assert = (condition: boolean, name: string, details?: string) => results.push({ name, passed: condition, details: condition ? undefined : details });
  try {
    await adminApi.getAdminDashboardData();
    assert(false, 'Phase 13: administration data is unavailable');
  } catch (error) {
    assert(error instanceof Error && error.message.includes('not exposed'), 'Phase 13: administration data is unavailable');
  }
  try {
    await adminApi.getUsers();
    assert(false, 'Phase 13: user provisioning is unavailable');
  } catch (error) {
    assert(error instanceof Error && error.message.includes('not exposed'), 'Phase 13: user provisioning is unavailable');
  }
  return results;
}
