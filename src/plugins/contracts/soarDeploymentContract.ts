import { PluginContractError } from './errors';
import { pluginContractRegistry } from './registry';
import type { JsonSchema, PluginInputContract } from './types';

export type SoarInputSource = 'CANONICAL_CLINICAL_ASSESSMENT' | 'CLINICIAN_ENTERED' | 'SYSTEM_CONTEXT' | 'BACKEND_PREPROCESSING';
export type BetaLactamaseStatus = 'POSITIVE' | 'NEGATIVE';

export const BETA_LACTAMASE_ENCODING_VERSION = 'SOAR_GSK_Phase9_Training_v1';
export const BETA_LACTAMASE_ENCODING_EVIDENCE = 'SOAR_GSK.zip:phase9_automated_training.py:86; SOAR_GSK.zip:phase10_evaluate_and_export.py:77';

export function encodeBetaLactamaseStatus(status: BetaLactamaseStatus): number {
  if (status === 'POSITIVE') return 1;
  if (status === 'NEGATIVE') return 0;
  throw new PluginContractError('CONTRACT_INVALID', `Unsupported beta-lactamase status: ${String(status)}.`);
}

export interface SoarDeploymentField {
  key: string;
  clinicalKey?: string;
  schema: JsonSchema;
  required: boolean;
  sourceClassification: 'CLINICIAN_REQUIRED' | 'UNKNOWN';
  evidenceReference: string;
}

export interface SoarDeploymentContract {
  deploymentId: string;
  organism: string;
  antimicrobial: string;
  contractVersion: string;
  requiredInputs: readonly SoarDeploymentField[];
  optionalInputs: readonly SoarDeploymentField[];
  artifactReferences: readonly string[];
}

const evidence = 'deployments/SOAR_GSK/<deployment>/feature_schema.json; deployment_info.json; docs/phase-22/Phase 22b soar deployment inspection.MD';

const countryValues: Record<string, readonly string[]> = {
  Cefixime_Haemophilus_influenzae: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Cefotaxime_Haemophilus_influenzae: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Cefpodoxime_Haemophilus_influenzae: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Ceftibuten_Haemophilus_influenzae: ['Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Ceftriaxone_Haemophilus_influenzae: ['Bulgaria', 'Croatia', 'Czech Republic', 'Greece', 'Italy', 'Kuwait', 'Romania', 'Russia', 'Slovak Republic', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Doxycycline_Streptococcus_pneumoniae: ['Italy', 'Kuwait', 'Pakistan', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Levofloxacin_Haemophilus_influenzae: ['Bulgaria', 'Croatia', 'Czech Republic', 'Greece', 'India', 'Italy', 'Kuwait', 'Pakistan', 'Romania', 'Russia', 'Serbia', 'Slovak Republic', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Tetracycline_Haemophilus_influenzae: ['India', 'Italy', 'Kuwait', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Tetracycline_Streptococcus_pneumoniae: ['Italy', 'Kuwait', 'Pakistan', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates', 'Vietnam'],
  Trimethoprim_Sulfa_Haemophilus_influenzae: ['Bulgaria', 'Croatia', 'Czech Republic', 'Greece', 'Italy', 'Kuwait', 'Romania', 'Russia', 'Serbia', 'Slovak Republic', 'Spain', 'Turkey', 'Ukraine', 'United Arab Emirates'],
};

const commonFields: readonly SoarDeploymentField[] = [
  { key: 'Age', schema: { type: 'number', title: 'Age' }, required: true, sourceClassification: 'CLINICIAN_REQUIRED', evidenceReference: evidence },
  { key: 'YearCollected', schema: { type: 'number', title: 'Year collected' }, required: true, sourceClassification: 'CLINICIAN_REQUIRED', evidenceReference: evidence },
  { key: 'Region', schema: { type: 'string', title: 'Region', enum: ['Asia', 'Europe', 'Middle East'] }, required: true, sourceClassification: 'CLINICIAN_REQUIRED', evidenceReference: evidence },
  { key: 'BodyLocation_Group', schema: { type: 'string', title: 'Body location group', enum: ['Blood', 'Other', 'Respiratory'] }, required: true, sourceClassification: 'CLINICIAN_REQUIRED', evidenceReference: evidence },
  { key: 'Country', schema: { type: 'string', title: 'Country' }, required: true, sourceClassification: 'CLINICIAN_REQUIRED', evidenceReference: evidence },
];

const betaLactamaseField: SoarDeploymentField = {
  key: 'Beta_Lactamase_enc',
  clinicalKey: 'BetaLactamaseStatus',
  schema: { type: 'number', title: 'Beta-lactamase encoded value' },
  required: true,
  sourceClassification: 'CLINICIAN_REQUIRED',
  evidenceReference: `${BETA_LACTAMASE_ENCODING_EVIDENCE}; mapping POS -> 1, NEG -> 0; version ${BETA_LACTAMASE_ENCODING_VERSION}`,
};

const deploymentInputs: Record<string, { organism: string; antimicrobial: string; betaLactamase: boolean }> = {
  Cefixime_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Cefixime', betaLactamase: true },
  Cefotaxime_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Cefotaxime', betaLactamase: true },
  Cefpodoxime_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Cefpodoxime', betaLactamase: true },
  Ceftibuten_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Ceftibuten', betaLactamase: true },
  Ceftriaxone_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Ceftriaxone', betaLactamase: true },
  Doxycycline_Streptococcus_pneumoniae: { organism: 'Streptococcus pneumoniae', antimicrobial: 'Doxycycline', betaLactamase: false },
  Levofloxacin_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Levofloxacin', betaLactamase: true },
  Tetracycline_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Tetracycline', betaLactamase: true },
  Tetracycline_Streptococcus_pneumoniae: { organism: 'Streptococcus pneumoniae', antimicrobial: 'Tetracycline', betaLactamase: false },
  Trimethoprim_Sulfa_Haemophilus_influenzae: { organism: 'Haemophilus influenzae', antimicrobial: 'Trimethoprim_Sulfa', betaLactamase: true },
};

export const SOAR_DEPLOYMENT_CONTRACTS: readonly SoarDeploymentContract[] = Object.entries(deploymentInputs).map(([deploymentId, definition]) => ({
  deploymentId,
  organism: definition.organism,
  antimicrobial: definition.antimicrobial,
  contractVersion: '23.0.0',
  requiredInputs: (definition.betaLactamase ? [...commonFields, betaLactamaseField] : commonFields).map((field) =>
    field.key === 'Country'
      ? { ...field, schema: { ...field.schema, enum: [...countryValues[deploymentId]] } }
      : field,
  ),
  optionalInputs: [],
  artifactReferences: [`deployments/SOAR_GSK/SOAR_GSK/deployment/${deploymentId}/final_model.pkl`, evidence],
}));

export function resolveSoarDeploymentContract(deploymentId: string): SoarDeploymentContract {
  const contract = SOAR_DEPLOYMENT_CONTRACTS.find((candidate) => candidate.deploymentId === deploymentId);
  if (!contract) throw new PluginContractError('CONTRACT_NOT_FOUND', `No verified SOAR contract exists for ${deploymentId}.`);
  return contract;
}

export function toSoarPluginContract(contract: SoarDeploymentContract): PluginInputContract {
  const properties = Object.fromEntries(contract.requiredInputs.map((field) => [field.clinicalKey || field.key, field.clinicalKey
    ? { type: 'string' as const, title: 'Beta-lactamase status', enum: ['POSITIVE', 'NEGATIVE'] }
    : field.schema]));
  return {
    pluginId: 'soar',
    contractId: `soar-${contract.deploymentId}`,
    contractVersion: contract.contractVersion,
    schemaVersion: '2020-12',
    displayName: `SOAR: ${contract.antimicrobial} / ${contract.organism}`,
    description: 'Verified deployment-specific SOAR inputs. Missing values must be explicitly supplied by an authorized clinician.',
    status: 'approved',
    provenance: {
      owner: 'PharmaTrybe SOAR artifact registry',
      source: 'Verified SOAR deployment artifacts and authoritative metadata',
      artifact: contract.artifactReferences.join('; '),
      artifactVersion: contract.contractVersion,
      approvedBy: 'Phase 23 evidence-backed contract extraction',
      approvedAt: '2026-09-07T00:00:00Z',
    },
    inputSchema: { $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object', properties, required: contract.requiredInputs.map((field) => field.clinicalKey || field.key), additionalProperties: false },
    uiSchema: { fields: contract.requiredInputs.map((field, index) => ({ field: field.clinicalKey || field.key, order: index + 1, widget: field.clinicalKey || field.schema.enum ? 'select' : field.schema.type === 'number' ? 'number' : 'text' })) },
    requiredFields: contract.requiredInputs.map((field) => field.clinicalKey || field.key),
    routingRequirements: ['deployment_id'],
    supportedExecutionMode: 'sync',
  };
}

export function ensureSoarDeploymentContractRegistered(deploymentId: string): PluginInputContract {
  const contract = toSoarPluginContract(resolveSoarDeploymentContract(deploymentId));
  pluginContractRegistry.registerIfAbsent(contract);
  return pluginContractRegistry.resolve('soar', contract.contractVersion);
}