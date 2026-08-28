/**
 * Phase 11: Static Plugin Registry Definitions
 * Defines static configuration metadata for known components in the AMR CDSS architecture.
 *
 * NOTE: As per Phase 11 specification, live backend telemetry is not exposed via standalone endpoints.
 * These definitions represent the known component architecture and are clearly marked as
 * registry metadata rather than live backend runtime status.
 */

import { PluginDefinition } from './pluginTypes';

export const CANONICAL_PLUGINS: PluginDefinition[] = [
  {
    id: 'who_knowledge',
    backendId: 'who_knowledge',
    name: 'WHO AWaRe Knowledge Base',
    category: 'knowledge',
    role: 'Evidence and guideline knowledge source',
    description:
      'Provides structured clinical guidance, pathogen spectra, diagnostic pathways, AWaRe classification tiers (Access, Watch, Reserve), monitoring schedules, and antimicrobial stewardship policies.',
    status: 'available',
    version: '0.1.0',
    modelVersion: 'WHO knowledge runtime',
    source: 'World Health Organization (WHO) AWaRe Antibiotic Book',
    capabilities: [
      'disease_lookup',
      'guideline_lookup',
      'recommendations',
      'evidence',
      'pathogens',
      'diagnostics',
      'monitoring',
      'follow_up',
      'referral',
      'stewardship',
    ],
    isCore: true,
    metadata: {
      updateCycle: 'Biennial',
      guidelineScope: 'Global Essential Medicines',
      storageType: 'Structured Clinical Knowledge Repository',
    },
    formSchema: [
      { id: 'diagnosis', label: 'Primary infection diagnosis', type: 'text', path: 'presentation.primaryDiagnosis', required: true, placeholder: 'e.g. Community-acquired pneumonia' },
      { id: 'severity', label: 'Clinical severity', type: 'select', path: 'presentation.severity', options: [
        { label: 'Non-severe', value: 'Non-severe' },
        { label: 'Moderate', value: 'Moderate' },
        { label: 'Severe', value: 'Severe' },
      ] },
      { id: 'infection_site', label: 'Infection site', type: 'text', path: 'presentation.infectionSite', placeholder: 'e.g. Lower respiratory tract' },
    ],
  },
  {
    id: 'soar_prediction',
    backendId: 'soar',
    name: 'SOAR Surveillance Prediction Model',
    category: 'prediction',
    role: 'Respiratory antimicrobial prediction / susceptibility contribution',
    description:
      'Predicts pathogen susceptibility and resistance probabilities for community-acquired respiratory tract pathogens based on regional longitudinal surveillance datasets.',
    status: 'available',
    version: '0.1.0',
    modelVersion: 'SOAR/GSK runtime',
    source: 'Survey of Antibiotic Resistance (SOAR) Longitudinal Program',
    capabilities: [
      'respiratory_stewardship',
      'susceptibility_prediction',
      'confidence_estimation',
      'regional_surveillance',
    ],
    isCore: false,
    metadata: {
      targetSyndromes: ['Community-Acquired Pneumonia (CAP)', 'Acute Otitis Media', 'COPD Exacerbation'],
      integrationBoundary: 'POST /api/v1/recommendations/generate',
      inferenceMode: 'Embedded Pipeline Execution',
    },
    formSchema: [
      { id: 'pathogen', label: 'Suspected pathogen', type: 'text', path: 'laboratory.suspectedPathogen', required: true, placeholder: 'e.g. Streptococcus pneumoniae' },
      { id: 'culture', label: 'Culture and microbiology result', type: 'textarea', path: 'laboratory.cultureResult', placeholder: 'Specimen, Gram stain, or preliminary culture result' },
    ],
  },
  {
    id: 'armd_prediction',
    backendId: 'armd',
    name: 'ARMD Deep Resistance Models',
    category: 'prediction',
    role: 'Antimicrobial resistance risk assessment and molecular MIC shift prediction',
    description:
      'Machine learning transformer models predicting genomic minimum inhibitory concentration (MIC) shifts, prior-exposure risks, and multidrug resistance probabilities.',
    status: 'available',
    version: '0.1.0',
    modelVersion: 'ARMD WP4 runtime',
    source: 'Antimicrobial Resistance Molecular Database & WP4 Engine',
    capabilities: [
      'resistance_prediction',
      'antibiotic_ranking',
      'shap_explainability',
      'genomic_mic_shifts',
    ],
    isCore: false,
    metadata: {
      targetPathogens: ['Escherichia coli', 'Klebsiella pneumoniae', 'Pseudomonas aeruginosa', 'MRSA'],
      integrationBoundary: 'POST /api/v1/recommendations/generate',
      inferenceMode: 'Embedded Pipeline Execution',
    },
    formSchema: [
      { id: 'age', label: 'Age (years)', type: 'number', path: 'demographics.age', required: true, step: '1' },
      { id: 'weight', label: 'Weight (kg)', type: 'number', path: 'demographics.weight', step: '0.1' },
      { id: 'egfr', label: 'eGFR (mL/min/1.73m2)', type: 'number', path: 'laboratory.egfr', step: '0.1', helpText: 'Used for resistance-risk and renal safety context.' },
      { id: 'prior_antibiotics', label: 'Antibiotic exposure in the last 90 days', type: 'checkbox', path: 'riskFactors.priorAntibiotics90Days' },
      { id: 'recent_hospitalization', label: 'Recent hospitalization', type: 'checkbox', path: 'riskFactors.recentHospitalization' },
    ],
  },
  {
    id: 'clinical_rules',
    name: 'Clinical Safety & Rules Engine',
    category: 'rules',
    role: 'Clinical safety, contraindication, allergy, renal dosing and stewardship rules',
    description:
      'Deterministic rule evaluation engine executing patient allergy cross-checking, renal clearance adjustments (eGFR / CrCl), pregnancy/lactation safety checks, and stewardship restrictions.',
    status: 'unknown',
    version: 'Not exposed by backend',
    modelVersion: 'Not exposed by backend',
    source: 'PharmaTrybe Clinical Rules Matrix',
    capabilities: [
      'allergy_verification',
      'renal_clearance_dosing',
      'pregnancy_lactation_rules',
      'contraindication_checking',
      'stewardship_policies',
    ],
    isCore: true,
    metadata: {
      executionPriority: 'Pre-Fusion Safety Gate',
      enforcementMode: 'Deterministic Constraint Verification',
    },
  },
  {
    id: 'decision_fusion',
    name: 'Decision Fusion Engine',
    category: 'fusion',
    role: 'Combines available clinical evidence and component outputs into the recommendation',
    description:
      'Synthesizes multi-source prediction probabilities, guideline recommendations, and clinical rule constraints into ranked primary and alternative antibiotic candidates.',
    status: 'unknown',
    version: 'Not exposed by backend',
    modelVersion: 'Not exposed by backend',
    source: 'PharmaTrybe Core CDSS Pipeline',
    capabilities: [
      'multi_source_evidence_fusion',
      'candidate_ranking',
      'conflict_resolution',
      'safety_gating',
    ],
    isCore: true,
    metadata: {
      fusionStrategy: 'Evidence-Weighted Safety-Constrained Synthesis',
      pipelineStage: 'Synthesis & Ranking',
    },
  },
  {
    id: 'explainability_engine',
    name: 'Explainability & Attribution Engine',
    category: 'explainability',
    role: 'Produces the evidence and reasoning representation associated with the recommendation',
    description:
      'Computes SHAP feature attribution weights, builds step-by-step clinical reasoning chains, formats evidence rankings, and generates human-readable clinical narratives.',
    status: 'unknown',
    version: 'Not exposed by backend',
    modelVersion: 'Not exposed by backend',
    source: 'PharmaTrybe Explainable AI (XAI) Subsystem',
    capabilities: [
      'shap_attribution_mapping',
      'reasoning_tree_generation',
      'clinical_narrative_synthesis',
      'evidence_ranking',
    ],
    isCore: true,
    metadata: {
      explainabilityMethod: 'TreeSHAP & Hierarchical Evidence Ranking',
      outputFormat: 'Evidence Drivers & Clinical Narrative',
    },
  },
  {
    id: 'audit_telemetry',
    name: 'Audit & Distributed Tracing Subsystem',
    category: 'audit',
    role: 'Provides traceability and reproducibility metadata',
    description:
      'Captures immutable distributed trace IDs, stage execution durations, component version provenance, and clinician review logs for regulatory compliance and auditability.',
    status: 'unknown',
    version: 'Not exposed by backend',
    modelVersion: 'Not exposed by backend',
    source: 'PharmaTrybe Governance & Telemetry Infrastructure',
    capabilities: [
      'distributed_tracing',
      'audit_trail_logging',
      'version_provenance',
      'execution_telemetry',
    ],
    isCore: true,
    metadata: {
      traceFormat: 'UUIDv4 Distributed Trace Envelope',
      auditRetention: 'Clinical Immutable Record',
    },
  },
];
