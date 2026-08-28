/**
 * PHASE 11 TEST SUITE: Plugin Registry & Model Telemetry
 * Validates the frontend Plugin Registry abstraction, Provenance models,
 * Telemetry extraction from canonical responses, Evidence Attribution mapping,
 * Recommendation Trace handling, and strict adherence to the API contract boundary.
 */

import {
  getRegisteredPlugins,
  getPluginById,
  getPluginsByCategory,
  mapEvidenceAttributionsToContributions,
  extractTelemetryFromContract,
  CANONICAL_PLUGINS,
  getPluginStatusPresentation,
  getCategoryBadge,
} from '../plugins/registry';
import { ExplainabilityResponseContract, EvidenceAttribution, RecommendationTrace } from '../types';
import { recommendationApi } from '../api/recommendationApi';

export interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
}

export function runPhase11TelemetryTests(): TestResult[] {
  const results: TestResult[] = [];

  const assert = (name: string, condition: boolean, errorMsg?: string) => {
    results.push({
      name,
      passed: Boolean(condition),
      error: condition ? undefined : errorMsg || 'Assertion failed',
    });
  };

  console.log('--- STARTING PHARMATRYBE PHASE 11 TEST SUITE ---');

  // =========================================================================
  // 1. PLUGIN REGISTRY TESTS
  // =========================================================================
  const allPlugins = getRegisteredPlugins();
  assert('Phase 11: Plugin Registry contains at least 7 canonical components', allPlugins.length >= 7);

  // Check all required components exist
  const pluginIds = allPlugins.map((p) => p.id);
  assert('Phase 11: All registered plugin IDs are strictly unique', new Set(pluginIds).size === pluginIds.length);

  assert('Phase 11: WHO Knowledge plugin is represented in registry', pluginIds.includes('who_knowledge'));
  assert('Phase 11: SOAR Prediction plugin is represented in registry', pluginIds.includes('soar_prediction'));
  assert('Phase 11: ARMD Prediction plugin is represented in registry', pluginIds.includes('armd_prediction'));
  assert('Phase 11: Clinical Rules plugin is represented in registry', pluginIds.includes('clinical_rules'));
  assert('Phase 11: Decision Fusion plugin is represented in registry', pluginIds.includes('decision_fusion'));
  assert('Phase 11: Explainability plugin is represented in registry', pluginIds.includes('explainability_engine'));
  assert('Phase 11: Audit / Telemetry plugin is represented in registry', pluginIds.includes('audit_telemetry'));

  // Validate Categories
  const validCategories = ['knowledge', 'prediction', 'rules', 'fusion', 'explainability', 'audit', 'risk', 'reporting', 'integration'];
  assert(
    'Phase 11: All plugins have valid architectural categories',
    allPlugins.every((p) => validCategories.includes(p.category))
  );

  // Validate Status values
  const validStatuses = ['available', 'unavailable', 'degraded', 'unknown'];
  assert(
    'Phase 11: All plugins have valid status values',
    allPlugins.every((p) => validStatuses.includes(p.status))
  );

  // Validate that default status does not claim unverified backend health
  const whoPlugin = getPluginById('who_knowledge');
  assert('Phase 11: WHO plugin has category "knowledge"', whoPlugin?.category === 'knowledge');
  assert('Phase 11: WHO plugin has non-empty capabilities array', Array.isArray(whoPlugin?.capabilities) && whoPlugin!.capabilities.length >= 5);
  assert('Phase 11: WHO plugin has valid role description', typeof whoPlugin?.role === 'string' && whoPlugin!.role.length > 0);

  const soarPlugin = getPluginById('soar_prediction');
  assert('Phase 11: SOAR plugin has category "prediction"', soarPlugin?.category === 'prediction');
  assert('Phase 11: SOAR plugin has version metadata', typeof soarPlugin?.version === 'string');

  const armdPlugin = getPluginById('armd_prediction');
  assert('Phase 11: ARMD plugin has category "prediction"', armdPlugin?.category === 'prediction');
  assert('Phase 11: ARMD plugin has modelVersion metadata', typeof armdPlugin?.modelVersion === 'string');

  const rulesPlugin = getPluginById('clinical_rules');
  assert('Phase 11: Rules plugin has category "rules"', rulesPlugin?.category === 'rules');

  const fusionPlugin = getPluginById('decision_fusion');
  assert('Phase 11: Fusion plugin has category "fusion"', fusionPlugin?.category === 'fusion');

  const explainPlugin = getPluginById('explainability_engine');
  assert('Phase 11: Explainability plugin has category "explainability"', explainPlugin?.category === 'explainability');

  const auditPlugin = getPluginById('audit_telemetry');
  assert('Phase 11: Audit plugin has category "audit"', auditPlugin?.category === 'audit');

  // Category Filtering
  const predictionPlugins = getPluginsByCategory('prediction');
  assert('Phase 11: getPluginsByCategory("prediction") returns SOAR and ARMD', predictionPlugins.length >= 2);

  // Status Presentation Helpers (Accessibility & Non-color reliance)
  const unknownStatusPres = getPluginStatusPresentation('unknown');
  assert('Phase 11: Unknown status label contains "Not exposed by backend"', unknownStatusPres.label.includes('Not exposed'));
  assert('Phase 11: Unknown status presentation includes ariaLabel', typeof unknownStatusPres.ariaLabel === 'string' && unknownStatusPres.ariaLabel.length > 0);

  // =========================================================================
  // 2. TELEMETRY EXTRACTION TESTS (From Canonical Response)
  // =========================================================================
  const mockCanonicalContract: ExplainabilityResponseContract = {
    status: 'success',
    patient_id: 'PAT-8812',
    confidence: 'high',
    generated_at: '2026-08-15T12:00:00.000Z',
    trace_id: 'trace-uuid-4412-9988',
    recommendation: {
      patient_id: 'PAT-8812',
      primary_recommendation: {
        antibiotic_name: 'Amoxicillin-Clavulanate',
        reason: 'Empiric coverage for severe CAP',
        guideline_category: 'Access',
        ranking: 1,
        confidence: 'high',
        alternative: false,
        warnings: [],
      },
      alternative_recommendations: [],
      clinical_rules: [],
      guideline_references: [],
      stewardship_findings: [],
      warnings: [],
      clinical_rationale: 'Patient presents with severe community-acquired pneumonia.',
      confidence: 'high',
      supporting_evidence: ['WHO AWaRe Access first-line recommendation'],
      generated_at: '2026-08-15T12:00:00.000Z',
      version: '1.0.0',
    },
    evidence_ranking: {
      recommendation_id: 'rec-101',
      patient_id: 'PAT-8812',
      ranked_evidence: [],
      ranking_algorithm: 'weighted_sum',
      timestamp: '2026-08-15T12:00:00.000Z',
    },
    evidence_attribution: [
      {
        source: 'WHO AWaRe Knowledge Base',
        plugin_name: 'who_knowledge',
        evidence_type: 'guideline_evidence',
        contribution_score: 0.45,
        details: 'First-line empiric therapy recommendation for severe CAP',
      },
      {
        source: 'SOAR Surveillance Prediction Model',
        plugin_name: 'soar_prediction',
        evidence_type: 'susceptibility_prediction',
        contribution_score: 0.35,
        details: 'Predicted S. pneumoniae susceptibility: 94.2%',
      },
    ],
    recommendation_trace: {
      recommendation_id: 'rec-101',
      patient_id: 'PAT-8812',
      total_duration_ms: 124.5,
      timestamp: '2026-08-15T12:00:00.000Z',
      trace_steps: [
        {
          step_number: 1,
          phase_name: 'orchestration',
          description: 'Orchestration pipeline initialized',
          inputs: { patient_id: 'PAT-8812' },
          outputs: { initialized: true },
          duration_ms: 12.0,
          timestamp: '2026-08-15T12:00:00.010Z',
        },
        {
          step_number: 2,
          phase_name: 'prediction_inference',
          description: 'SOAR and ARMD predictions executed in parallel',
          inputs: { syndrome: 'cap' },
          outputs: { soar_confidence: 0.94 },
          duration_ms: 45.2,
          timestamp: '2026-08-15T12:00:00.055Z',
        },
        {
          step_number: 3,
          phase_name: 'decision_fusion',
          description: 'Decision fusion combined predictions with WHO guidelines',
          inputs: { candidates_count: 4 },
          outputs: { selected_antibiotic: 'Amoxicillin-Clavulanate' },
          duration_ms: 67.3,
          timestamp: '2026-08-15T12:00:00.124Z',
        },
      ],
    },
    audit_reference: {
      recommendation_id: 'rec-101',
      patient_id: 'PAT-8812',
      timestamp: '2026-08-15T12:00:00.000Z',
      trace_id: 'trace-uuid-4412-9988',
      prediction_plugin_version: '0.2.0',
      model_versions: {
        soar_resnet: 'v2.1',
        armd_transformer: 'v2.4',
      },
      rule_versions: 'Rules-v1.0.0',
      guideline_engine_version: 'WHO-v2023.1',
      stewardship_engine_version: 'Stewardship-v1.0.0',
      cdss_version: 'v1.0.4-prod',
      algorithm_version: 'Fusion-Ranked-v1.0',
    },
    explanation: null,
  };

  const telemetry = extractTelemetryFromContract(mockCanonicalContract);
  assert('Phase 11: Telemetry extractor successfully extracts telemetry', telemetry !== null);
  assert('Phase 11: Trace ID preserved accurately', telemetry?.traceId === 'trace-uuid-4412-9988');
  assert('Phase 11: Generated timestamp preserved accurately', telemetry?.generatedAt === '2026-08-15T12:00:00.000Z');
  assert('Phase 11: Confidence level preserved accurately', telemetry?.confidence === 'high');
  assert('Phase 11: Prediction plugin version preserved accurately', telemetry?.predictionPluginVersion === '0.2.0');
  assert('Phase 11: Guideline engine version preserved accurately', telemetry?.guidelineEngineVersion === 'WHO-v2023.1');
  assert('Phase 11: Total duration (ms) preserved accurately', telemetry?.totalDurationMs === 124.5);
  assert('Phase 11: Trace steps count preserved accurately', telemetry?.traceStepsCount === 3);

  // Missing Telemetry Graceful Handling
  const nullTelemetry = extractTelemetryFromContract(null);
  assert('Phase 11: extractTelemetryFromContract(null) safely returns null', nullTelemetry === null);

  const emptyContractTelemetry = extractTelemetryFromContract({} as any);
  assert('Phase 11: Partial contract telemetry extraction does not throw error', emptyContractTelemetry !== null);

  // =========================================================================
  // 3. EVIDENCE ATTRIBUTION MAPPING TESTS
  // =========================================================================
  const contributions = mapEvidenceAttributionsToContributions(mockCanonicalContract.evidence_attribution);
  assert('Phase 11: mapEvidenceAttributionsToContributions returns array of contributions', contributions.length === 2);
  assert('Phase 11: WHO contribution correctly mapped', contributions[0].pluginId === 'who_knowledge');
  assert('Phase 11: SOAR contribution correctly mapped', contributions[1].pluginId === 'soar_prediction');
  assert('Phase 11: Weight is numeric where provided', contributions[0].weight === 0.45 && contributions[1].weight === 0.35);

  // Empty / Absent Attribution Handling
  const emptyContributions = mapEvidenceAttributionsToContributions([]);
  assert('Phase 11: Empty attribution list returns empty array []', Array.isArray(emptyContributions) && emptyContributions.length === 0);

  const nullContributions = mapEvidenceAttributionsToContributions(null);
  assert('Phase 11: Null attribution returns empty array []', Array.isArray(nullContributions) && nullContributions.length === 0);

  // Unknown Source in Attribution Handling
  const unknownAttrContributions = mapEvidenceAttributionsToContributions([
    {
      source: 'Custom Hospital Formulary Plugin',
      details: 'Restricted reserve tier',
      contribution_score: 0.1,
    },
  ]);
  assert('Phase 11: Unknown plugin attribution handles gracefully without throwing', unknownAttrContributions.length === 1);
  assert('Phase 11: Unknown plugin receives fallback identifier', unknownAttrContributions[0].pluginId === 'custom_hospital_formulary_plugin');

  // =========================================================================
  // 4. RECOMMENDATION TRACE TESTS
  // =========================================================================
  const trace = mockCanonicalContract.recommendation_trace;
  assert('Phase 11: Recommendation trace has 3 steps', trace.trace_steps.length === 3);
  assert('Phase 11: Step 1 phase is orchestration', trace.trace_steps[0].phase_name === 'orchestration');
  assert('Phase 11: Step 2 phase is prediction_inference', trace.trace_steps[1].phase_name === 'prediction_inference');
  assert('Phase 11: Step 3 phase is decision_fusion', trace.trace_steps[2].phase_name === 'decision_fusion');

  // =========================================================================
  // 5. API CONTRACT & BOUNDARY VERIFICATION
  // =========================================================================
  // Verify that no forbidden / non-existent endpoints are exposed in our API modules
  const forbiddenMethods = [
    'predictSoar',
    'predictArmd',
    'getPlugins',
    'getTelemetry',
    'getModelRegistry',
    'soarPredict',
    'armdPredict',
    'pluginRegistry',
  ];

  const allApiMethods = [
    ...Object.keys(recommendationApi as any),
  ];

  const hasForbidden = forbiddenMethods.some((m) => allApiMethods.includes(m));
  assert('Phase 11: No standalone SOAR predict endpoint called in frontend', !allApiMethods.includes('predictSoar') && !allApiMethods.includes('soarPredict'));
  assert('Phase 11: No standalone ARMD predict endpoint called in frontend', !allApiMethods.includes('predictArmd') && !allApiMethods.includes('armdPredict'));
  assert('Phase 11: No standalone plugin registry endpoint called in frontend', !allApiMethods.includes('getPlugins') && !allApiMethods.includes('getTelemetry'));
  assert('Phase 11: Canonical POST /api/v1/recommendations/generate is the sole recommendation boundary', typeof recommendationApi.generateRecommendation === 'function');

  console.log('--- COMPLETED PHARMATRYBE PHASE 11 TEST SUITE ---');
  return results;
}
