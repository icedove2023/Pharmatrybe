import { runR8SessionLifecycleTests } from './src/__tests__/r8_session_lifecycle.test.ts';

const results = await runR8SessionLifecycleTests();
console.log(JSON.stringify(results, null, 2));
const failed = results.filter((r) => !r.passed);
if (failed.length > 0) {
  console.error(`FAILED: ${failed.length} assertions`);
  process.exit(1);
}
console.log(`PASS: ${results.length} assertions`);
