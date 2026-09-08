import { PluginContractError } from './errors';
import { encodeBetaLactamaseStatus, resolveSoarDeploymentContract, type SoarDeploymentContract, type SoarInputSource } from './soarDeploymentContract';
import { validateFormValues } from './validation';

export interface SoarInputProvenance { field: string; value: unknown; source: SoarInputSource }
export interface SoarMissingInput { field: string; reason: 'REQUIRED_INPUT_MISSING' | 'UNSUPPORTED_MAPPING' }
export interface SoarInputResolution {
  deploymentId: string;
  resolvedInputs: Record<string, unknown>;
  missingRequiredInputs: SoarMissingInput[];
  provenance: Record<string, SoarInputProvenance>;
  isComplete: boolean;
}

export interface SoarInputResolutionRequest {
  deploymentId: string;
  canonicalClinicalData?: Record<string, unknown>;
  clinicianEntered?: Record<string, unknown>;
}

export function resolveSoarInputs(request: SoarInputResolutionRequest): SoarInputResolution {
  const contract = resolveSoarDeploymentContract(request.deploymentId);
  const resolvedInputs: Record<string, unknown> = {};
  const provenance: Record<string, SoarInputProvenance> = {};
  const missingRequiredInputs: SoarMissingInput[] = [];

  for (const field of contract.requiredInputs) {
    const canonicalValue = request.canonicalClinicalData?.[field.key];
    const clinicianKey = field.clinicalKey || field.key;
    const clinicianValue = request.clinicianEntered?.[clinicianKey];
    if (field.key === 'Beta_Lactamase_enc' && request.clinicianEntered?.[field.key] !== undefined) {
      missingRequiredInputs.push({ field: field.key, reason: 'UNSUPPORTED_MAPPING' });
      continue;
    }
    const sourceValue = canonicalValue !== undefined ? canonicalValue : clinicianValue;
    if (field.key === 'Beta_Lactamase_enc' && sourceValue !== undefined && sourceValue !== null && sourceValue !== 'POSITIVE' && sourceValue !== 'NEGATIVE') {
      missingRequiredInputs.push({ field: field.key, reason: 'UNSUPPORTED_MAPPING' });
      continue;
    }
    const value = field.key === 'Beta_Lactamase_enc' && typeof sourceValue === 'string'
      ? encodeBetaLactamaseStatus(sourceValue as 'POSITIVE' | 'NEGATIVE')
      : sourceValue;
    if (value === undefined || value === null || value === '') {
      missingRequiredInputs.push({ field: field.key, reason: 'REQUIRED_INPUT_MISSING' });
      continue;
    }
    const source: SoarInputSource = canonicalValue !== undefined ? 'CANONICAL_CLINICAL_ASSESSMENT' : 'CLINICIAN_ENTERED';
    resolvedInputs[field.key] = value;
    provenance[field.key] = { field: field.key, value, source };
  }

  return { deploymentId: request.deploymentId, resolvedInputs, missingRequiredInputs, provenance, isComplete: missingRequiredInputs.length === 0 };
}

export function buildSoarExecutionPayload(resolution: SoarInputResolution, contract: SoarDeploymentContract): { routing_context: { deployment_id: string }; input_payload: Record<string, unknown> } {
  if (!resolution.isComplete) throw new PluginContractError('PLUGIN_ADAPTER_ERROR', `SOAR requires additional information: ${resolution.missingRequiredInputs.map((item) => item.field).join(', ')}.`);
  if (resolution.deploymentId !== contract.deploymentId) throw new PluginContractError('PLUGIN_ADAPTER_ERROR', 'SOAR deployment and input contract identities do not match.');
  const validation = validateFormValues(toSoarSchema(contract), resolution.resolvedInputs);
  if (!validation.valid) throw new PluginContractError('PLUGIN_ADAPTER_ERROR', `SOAR input validation failed: ${validation.issues.map((issue) => issue.path).join(', ')}.`);
  return { routing_context: { deployment_id: contract.deploymentId }, input_payload: resolution.resolvedInputs };
}

function toSoarSchema(contract: SoarDeploymentContract) {
  return {
    type: 'object' as const,
    properties: Object.fromEntries(contract.requiredInputs.map((field) => [field.key, field.schema])),
    required: contract.requiredInputs.map((field) => field.key),
    additionalProperties: false,
  };
}