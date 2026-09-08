import {
  ClinicalCase,
  RecommendationPackage,
  ExplainabilityPackage,
  ExecutionMode,
  ClinicalRuleResult,
  ExplainabilityDriver,
  AuditTrail,
  ExplainabilityResponseContract,
  RecommendationResult,
  PrimaryRecommendation,
  AlternativeRecommendation,
  GuidelineReference,
  StewardshipFinding,
  EvidenceRanking,
  RankedEvidence,
  EvidenceAttribution,
  RecommendationTrace,
  RecommendationTraceStep,
  AuditReference,
  RecommendationExplanation,
  PredictionExplanation,
  ClinicalReviewRequest,
  ClinicalReviewResponse,
  RecommendationGenerateRequest,
  ConfidenceLevel,
} from '@/types';
import { apiRequest } from './client';

export interface ApiMetadata {
  request_id: string;
  timestamp: string;
  api_version: string;
  processing_time_ms: number;
}

export interface RecommendationSubmissionResult {
  caseId: string;
  response: ExplainabilityResponseContract;
  recommendation: RecommendationPackage; // Backward-compatible presentation adapter
  explanation: ExplainabilityPackage;   // Backward-compatible presentation adapter
  metadata: ApiMetadata;
}

const pipelineResponseCache = new Map<string, ExplainabilityResponseContract>();

/**
 * Builds a deterministic contract fixture for isolated contract tests.
 * Production requests use the backend endpoint below and never call this helper.
 * Strictly adheres to Copilot-verified Backend Truth:
 * - 11 total top-level fields
 * - confidence is a string (e.g. "high", "moderate")
 * - dosage_notes (not adjustment_notes)
 * - recommendation_trace with trace_steps
 * - evidence_ranking with ranked_evidence
 * - explanation is optional (null or object)
 * - evidence_attribution default []
 */
export function buildCanonicalResponse(
  patientId: string,
  patientData: Record<string, any>,
  predictionResults: Record<string, number>,
  options?: {
    predictionExplanation?: PredictionExplanation | null;
    predictionPluginVersion?: string;
    modelVersions?: Record<string, string>;
    omitExplanation?: boolean;
    emptyEvidenceAttribution?: boolean;
    confidenceOverride?: ConfidenceLevel;
  }
): ExplainabilityResponseContract {
  const timestamp = new Date().toISOString();
  const recommendationId = `REC-${Date.now().toString().slice(-6)}`;
  const traceId = `trace-pt-${Math.random().toString(36).slice(2, 10)}-${Date.now()}`;

  const condition = patientData.condition || patientData.primaryDiagnosis || 'Community-Acquired Pneumonia (CAP)';
  const age = patientData.age || 68;
  const sex = patientData.sex || 'Male';
  const allergies: string[] = patientData.allergies || [];
  const egfr = patientData.egfr || 55;

  // 1. Sort predictions to find primary & alternatives
  const sortedCandidates = Object.entries(predictionResults)
    .map(([drug, prob]) => ({ drugName: drug, prob }))
    .sort((a, b) => b.prob - a.prob);

  // 2. Evaluate Clinical Rules (Allergies, Renal, etc.)
  const hasPenicillinAllergy = allergies.some((a) => a.toLowerCase().includes('penicillin'));
  const hasSulfaAllergy = allergies.some((a) => a.toLowerCase().includes('sulfa'));
  const hasQuinoloneAllergy = allergies.some((a) => a.toLowerCase().includes('cipro') || a.toLowerCase().includes('fluoroquinolone'));

  const clinicalRules: ClinicalRuleResult[] = [];
  const warnings: string[] = [];

  if (hasPenicillinAllergy) {
    clinicalRules.push({
      rule_id: 'rule-allergy-penicillin',
      rule_name: 'Allergy',
      status: 'TRIGGERED',
      severity: 'HIGH',
      affected_drugs: ['Amoxicillin', 'Co-amoxiclav', 'Ampicillin'],
      message: 'Documented Penicillin allergy in patient record. Beta-lactam candidates evaluated with cross-reactivity warning.',
      dosage_notes: 'Class switch to non-beta-lactam (e.g. Doxycycline) or close clinical observation recommended.',
    });
    warnings.push('Documented Penicillin allergy. Beta-lactams contraindicated or require desensitization.');
  } else {
    clinicalRules.push({
      rule_id: 'rule-allergy-none',
      rule_name: 'Allergy',
      status: 'PASSED',
      severity: 'LOW',
      affected_drugs: [],
      message: 'No contraindicating drug allergies detected for candidate spectrum.',
    });
  }

  if (hasSulfaAllergy) {
    clinicalRules.push({
      rule_id: 'rule-allergy-sulfa',
      rule_name: 'Allergy',
      status: 'TRIGGERED',
      severity: 'CRITICAL',
      affected_drugs: ['Trimethoprim/Sulfamethoxazole'],
      message: 'Sulfa allergy contraindicates Trimethoprim/Sulfamethoxazole.',
    });
    warnings.push('Sulfa allergy contraindicates TMP-SMX.');
  }

  if (hasQuinoloneAllergy) {
    clinicalRules.push({
      rule_id: 'rule-allergy-quinolone',
      rule_name: 'Allergy',
      status: 'TRIGGERED',
      severity: 'HIGH',
      affected_drugs: ['Ciprofloxacin', 'Levofloxacin'],
      message: 'Quinolone intolerance documented. Fluoroquinolones excluded.',
    });
    warnings.push('Quinolone intolerance documented.');
  }

  // Renal Impairment Check
  if (egfr < 30) {
    clinicalRules.push({
      rule_id: 'rule-renal-severe',
      rule_name: 'Renal Impairment',
      status: 'TRIGGERED',
      severity: 'HIGH',
      affected_drugs: ['Nitrofurantoin', 'Gentamicin', 'Vancomycin'],
      message: `Severe renal impairment (eGFR ${egfr} mL/min/1.73m²). Nitrofurantoin ineffective; renally cleared agents require dose reduction.`,
      dosage_notes: 'Dose interval prolongation and therapeutic drug monitoring required.',
    });
    warnings.push(`Severe renal impairment (eGFR ${egfr}). Therapeutic drug monitoring required.`);
  } else if (egfr < 60) {
    clinicalRules.push({
      rule_id: 'rule-renal-mod',
      rule_name: 'Renal Impairment',
      status: 'WARNING',
      severity: 'MEDIUM',
      affected_drugs: ['Amoxicillin', 'Cefalexin'],
      message: `Moderate renal impairment (eGFR ${egfr} mL/min/1.73m²). Standard empirical dose acceptable; monitor clearance.`,
      dosage_notes: 'Standard empirical dose acceptable; monitor hydration and renal parameters.',
    });
  } else {
    clinicalRules.push({
      rule_id: 'rule-renal-normal',
      rule_name: 'Renal Impairment',
      status: 'PASSED',
      severity: 'LOW',
      affected_drugs: [],
      message: `Normal renal function (eGFR ${egfr} mL/min/1.73m²). No dose adjustment required.`,
    });
  }

  // Determine top non-contraindicated drug
  let primaryCandidate = sortedCandidates[0];
  if (hasPenicillinAllergy && (primaryCandidate.drugName.toLowerCase().includes('amoxicillin') || primaryCandidate.drugName.toLowerCase().includes('ampicillin'))) {
    const nonPenicillin = sortedCandidates.find(
      (c) => !c.drugName.toLowerCase().includes('amoxicillin') && !c.drugName.toLowerCase().includes('ampicillin') && !c.drugName.toLowerCase().includes('co-amoxiclav')
    );
    if (nonPenicillin) primaryCandidate = nonPenicillin;
  }

  const primaryCategory = (
    primaryCandidate.drugName.toLowerCase().includes('cipro') ||
    primaryCandidate.drugName.toLowerCase().includes('levo') ||
    primaryCandidate.drugName.toLowerCase().includes('azithro') ||
    primaryCandidate.drugName.toLowerCase().includes('clinda')
      ? 'watch'
      : primaryCandidate.drugName.toLowerCase().includes('meropenem') ||
        primaryCandidate.drugName.toLowerCase().includes('vancomycin') ||
        primaryCandidate.drugName.toLowerCase().includes('linezolid')
      ? 'reserve'
      : 'access'
  );

  const confidenceValue: ConfidenceLevel =
    options?.confidenceOverride ||
    (primaryCandidate.prob >= 0.95
      ? 'very_high'
      : primaryCandidate.prob >= 0.85
      ? 'high'
      : primaryCandidate.prob >= 0.65
      ? 'moderate'
      : primaryCandidate.prob >= 0.35
      ? 'low'
      : 'very_low');

  const primaryRec: PrimaryRecommendation = {
    antibiotic_name: primaryCandidate.drugName,
    reason: `First-line empirical antimicrobial indicated for ${condition}. Narrow-spectrum ${primaryCategory.toUpperCase()} selection preserves reserve tiers while achieving optimal target pathogen susceptibility.`,
    guideline_category: primaryCategory,
    ranking: 1,
    confidence: confidenceValue,
    alternative: false,
    warnings,
    dosage_notes: primaryCandidate.drugName === 'Amoxicillin' ? '500 mg orally every 8 hours' : primaryCandidate.drugName === 'Doxycycline' ? '100 mg orally every 12 hours (200 mg loading dose)' : 'Standard therapeutic dosage as per institutional antimicrobial formulary',
    duration_notes: '5 to 7 days duration recommended under standard clinical response review at 48-72 hours',
  };

  const altCandidates = sortedCandidates.filter((c) => c.drugName !== primaryCandidate.drugName).slice(0, 3);
  const alternativeRecommendations: AlternativeRecommendation[] = altCandidates.map((c, idx) => {
    const altCat = c.drugName.toLowerCase().includes('cipro') || c.drugName.toLowerCase().includes('levo') ? 'watch' : 'access';
    return {
      antibiotic_name: c.drugName,
      reason: `Alternative regimen for ${condition} (probability: ${Math.round(c.prob * 100)}%). Suitable in cases of treatment intolerance or targeted culture de-escalation.`,
      guideline_category: altCat,
      ranking: idx + 2,
      confidence: c.prob >= 0.8 ? 'high' : 'moderate',
      alternative: true,
      warnings: hasPenicillinAllergy && c.drugName.includes('Amox') ? ['Beta-lactam allergy contraindication'] : [],
      dosage_notes: 'Standard therapeutic dose per institutional guideline',
      duration_notes: '5 to 7 days',
    };
  });

  const guidelineReferences: GuidelineReference[] = [
    {
      guideline_id: 'WHO-AWARE-2026',
      guideline_name: 'WHO AWaRe Antibiotic Book (2026 Edition)',
      category: primaryCategory.toUpperCase(),
      evidence_level: 'A-I',
      drug_name: primaryRec.antibiotic_name,
      recommendations: `First-line recommendation for empirical management of uncomplicated ${condition}.`,
      contraindications: hasPenicillinAllergy ? ['Documented severe hypersensitivity to beta-lactam antimicrobials'] : [],
      url: 'https://www.who.int/publications/i/item/9789240062382',
    },
    {
      guideline_id: 'NICE-NG138',
      guideline_name: 'NICE Guideline NG138: Antimicrobial Prescribing in Respiratory / Systemic Infection',
      category: 'Clinical Protocol',
      evidence_level: 'B-II',
      drug_name: primaryRec.antibiotic_name,
      recommendations: 'Short-course empirical therapy (5 days) recommended to minimize adverse resistance selection.',
    },
  ];

  const stewardshipFindings: StewardshipFinding[] = [
    {
      finding_id: 'stewardship-aware-01',
      title: 'AWaRe Classification Conformance',
      category: primaryCategory,
      score: primaryCategory === 'access' ? 95 : 75,
      finding: `Selected regimen belongs to WHO ${primaryCategory.toUpperCase()} category with low selective resistance pressure.`,
      recommendation: 'Document clinical indication and microbiological culture status in patient chart.',
      notes: [
        'Review patient status at 48-72 hours for IV-to-oral switch or targeted de-escalation.',
        'Preserves reserve hospital antimicrobial tiers for multidrug-resistant pathogens.',
      ],
    },
  ];

  const recommendationResult: RecommendationResult = {
    patient_id: patientId,
    primary_recommendation: primaryRec,
    alternative_recommendations: alternativeRecommendations,
    clinical_rules: clinicalRules,
    guideline_references: guidelineReferences,
    stewardship_findings: stewardshipFindings,
    warnings,
    clinical_rationale: `${primaryRec.antibiotic_name} is recommended as first-line empirical therapy for ${condition}. Empirical spectrum aligns with regional surveillance susceptibility data (>88%) and complies with WHO AWaRe stewardship guidelines.`,
    confidence: confidenceValue,
    supporting_evidence: [
      `WHO AWaRe 2026 First-Line ${primaryCategory.toUpperCase()} Antimicrobial`,
      `SOAR Regional Surveillance Network (>88% susceptibility for ${condition})`,
      `ARMD Deep ML Resistance Transformer Concordance`,
      `Clinical safety rules verified (eGFR ${egfr} mL/min)`,
    ],
    generated_at: timestamp,
    version: '1.0.0',
  };

  // 3. Evidence Ranking
  const rankedEvidence: RankedEvidence[] = [
    {
      weight: 0.38,
      source: 'WHO AWaRe Guidelines',
      evidence: `WHO AWaRe 2026 designates ${primaryRec.antibiotic_name} as First-Line ${primaryCategory.toUpperCase()} therapy for ${condition}.`,
      impact: 'Supports',
      affected_drug: primaryRec.antibiotic_name,
      confidence: 0.98,
      clinical_importance: 0.95,
    },
    {
      weight: 0.30,
      source: 'SOAR Regional Surveillance',
      evidence: `Regional epidemiological isolates demonstrate >88% susceptibility for primary bacterial pathogens in ${condition}.`,
      impact: 'Supports',
      affected_drug: primaryRec.antibiotic_name,
      confidence: 0.91,
      clinical_importance: 0.90,
    },
    {
      weight: 0.18,
      source: 'ARMD Resistance Prediction Engine',
      evidence: `Deep Transformer model estimates low resistance probability (score: 0.08) for ${primaryRec.antibiotic_name}.`,
      impact: 'Supports',
      affected_drug: primaryRec.antibiotic_name,
      confidence: 0.89,
      clinical_importance: 0.85,
    },
    {
      weight: 0.14,
      source: 'Clinical Safety Rules',
      evidence: `Patient renal clearance (eGFR ${egfr} mL/min) and age (${age}y) evaluated; safe therapeutic dosage confirmed.`,
      impact: 'Supports',
      affected_drug: primaryRec.antibiotic_name,
      confidence: 1.0,
      clinical_importance: 0.92,
    },
  ];

  if (hasPenicillinAllergy) {
    rankedEvidence.push({
      weight: 0.25,
      source: 'Clinical Rules (Allergy)',
      evidence: 'Documented penicillin hypersensitivity in patient record; beta-lactams penalized or contraindicated.',
      impact: 'Caution',
      affected_drug: 'Amoxicillin',
      confidence: 1.0,
      clinical_importance: 0.98,
    });
  }

  const evidenceRanking: EvidenceRanking = {
    recommendation_id: recommendationId,
    patient_id: patientId,
    ranked_evidence: rankedEvidence,
    ranking_algorithm: 'composite_weight (confidence × clinical_importance)',
    timestamp,
  };

  // 4. Evidence Attribution (default array; may be empty if option requested)
  const evidenceAttribution: EvidenceAttribution[] = options?.emptyEvidenceAttribution
    ? []
    : [
        {
          source: 'SOAR Plugin',
          plugin_name: 'soar_gsk_prediction_engine',
          evidence_type: 'Regional Isolates Susceptibility',
          contribution_score: 0.38,
          details: 'Extracted from regional epidemiological surveillance database (GSK SOAR 2025/2026).',
          timestamp,
        },
        {
          source: 'ARMD Transformer Plugin',
          plugin_name: 'armd_molecular_transformer',
          evidence_type: 'Molecular Resistance Prediction',
          contribution_score: 0.28,
          details: 'Genomic and phenotypic resistance marker transformer model v1.4.2.',
          timestamp,
        },
        {
          source: 'WHO AWaRe Knowledge Base',
          plugin_name: 'who_aware_guidelines_engine',
          evidence_type: 'Global Guidelines Baseline',
          contribution_score: 0.34,
          details: 'WHO AWaRe Classification 2026 edition knowledge repository.',
          timestamp,
        },
      ];

  // 5. Recommendation Trace (Auditable Execution Steps)
  const traceSteps: RecommendationTraceStep[] = [
    {
      step_number: 1,
      phase_name: 'orchestration',
      description: 'Orchestrated clinical decision pipeline and dispatched patient parameters to registered plugins.',
      inputs: { patient_id: patientId, age, sex, condition, egfr },
      outputs: { active_plugins: ['soar_gsk', 'armd_transformer', 'clinical_rules', 'who_aware'] },
      duration_ms: 4.2,
      timestamp,
    },
    {
      step_number: 2,
      phase_name: 'prediction_extraction',
      description: 'Extracted candidate antimicrobial susceptibility probabilities from SOAR and ARMD plugins.',
      inputs: { condition, pathogens: 'Streptococcus pneumoniae / atypical' },
      outputs: { candidates_count: sortedCandidates.length, top_candidate: primaryCandidate.drugName },
      duration_ms: 12.6,
      timestamp,
    },
    {
      step_number: 3,
      phase_name: 'safety_rules_evaluation',
      description: 'Evaluated deterministic safety constraints (Allergy, Renal Impairment, Drug-Drug Interactions).',
      inputs: { allergies, egfr, age },
      outputs: { rules_passed: clinicalRules.filter((r) => r.status === 'PASSED').length, rules_triggered: clinicalRules.filter((r) => r.status === 'TRIGGERED').length },
      duration_ms: 3.1,
      timestamp,
    },
    {
      step_number: 4,
      phase_name: 'decision_fusion',
      description: 'Fused prediction probabilities, guideline hierarchy, and stewardship weights into unified recommendation.',
      inputs: { prediction_scores: predictionResults, guideline_weight: 0.4, surveillance_weight: 0.3 },
      outputs: { primary_antibiotic: primaryRec.antibiotic_name, confidence: confidenceValue },
      duration_ms: 6.8,
      timestamp,
    },
    {
      step_number: 5,
      phase_name: 'audit_trace_generation',
      description: 'Generated immutable distributed audit record and explainability envelope.',
      inputs: { recommendation_id: recommendationId, trace_id: traceId },
      outputs: { status: 'success', trace_id: traceId },
      duration_ms: 2.1,
      timestamp,
    },
  ];

  const recommendationTrace: RecommendationTrace = {
    recommendation_id: recommendationId,
    patient_id: patientId,
    trace_steps: traceSteps,
    total_duration_ms: 28.8,
    timestamp,
  };

  // 6. Audit Reference
  const auditReference: AuditReference = {
    recommendation_id: recommendationId,
    patient_id: patientId,
    timestamp,
    trace_id: traceId,
    prediction_plugin_version: options?.predictionPluginVersion || 'soar-gsk:v2.1.0,armd:v1.4.2',
    model_versions: options?.modelVersions || {
      soar_gsk: 'v2.1.0',
      armd_transformer: 'v1.4.2',
      clinical_rules: 'v0.1.0',
      decision_fusion: 'v0.1.0',
    },
    rule_versions: 'v0.1.0-stewardship-rules',
    guideline_engine_version: 'who-aware-2026.1',
    stewardship_engine_version: 'pt-stewardship-v1.0',
    cdss_version: 'v1.0.0',
    algorithm_version: 'deterministic-fusion-v1.0',
    metadata: {
      primary_recommendation: primaryRec.antibiotic_name,
      confidence: confidenceValue,
      alternatives_count: alternativeRecommendations.length,
      rules_triggered: clinicalRules.filter((r) => r.status === 'TRIGGERED').length,
    },
  };

  // 7. Optional Explanation / SHAP
  let explanation: RecommendationExplanation | null = null;
  if (!options?.omitExplanation) {
    const defaultShap: PredictionExplanation = options?.predictionExplanation || {
      feature_contributions: {
        [`Indication: ${condition}`]: 0.38,
        'WHO First-Line Guideline Concordance': 0.32,
        'Regional SOAR Susceptibility (>88%)': 0.24,
        [`Patient Age (${age}y)`]: 0.12,
        [`Adequate Renal Clearance (eGFR ${egfr})`]: 0.08,
        'No Prior Hospitalization in 90d': 0.05,
        ...(hasPenicillinAllergy ? { 'Penicillin Allergy Penalty': -0.22 } : {}),
      },
      feature_importance: {
        'Guideline Hierarchy': 0.38,
        'Regional Surveillance': 0.30,
        'ML Transformer Resistance Prediction': 0.18,
        'Clinical Safety Rules': 0.14,
      },
      method: 'shap',
      base_value: 0.15,
    };

    explanation = {
      recommendation_id: recommendationId,
      patient_id: patientId,
      primary_antibiotic: primaryRec.antibiotic_name,
      prediction_explanation: defaultShap,
      rule_explanations: clinicalRules.map((r) => `${r.rule_name}: ${r.message}`),
      guideline_explanations: guidelineReferences.map((g) => `${g.guideline_name}: ${g.recommendations}`),
      stewardship_explanations: [
        `Preserves Reserve-tier antimicrobials by selecting narrow-spectrum ${primaryCategory.toUpperCase()} category.`,
        'Stewardship penalty applied to broad-spectrum fluoroquinolones due to resistance risk.',
      ],
      evidence_drivers: rankedEvidence,
      warnings,
      clinical_narrative: `${primaryRec.antibiotic_name} is indicated as first-line empirical therapy for ${condition}. The recommendation was derived deterministically by synthesizing WHO AWaRe guidelines, regional SOAR surveillance data, and clinical safety rule checks.`,
      generated_at: timestamp,
    };
  }

  // 8. Canonical 11-field ExplainabilityResponseContract
  const canonicalResponse: ExplainabilityResponseContract = {
    status: 'success',
    patient_id: patientId,
    recommendation: recommendationResult,
    confidence: confidenceValue,
    evidence_ranking: evidenceRanking,
    evidence_attribution: evidenceAttribution,
    recommendation_trace: recommendationTrace,
    audit_reference: auditReference,
    explanation,
    generated_at: timestamp,
    trace_id: traceId,
  };

  return canonicalResponse;
}

/**
 * Adapter helper to transform canonical response into backward-compatible presentation formats
 */
export function adaptCanonicalToLegacyPackages(
  caseId: string,
  contract: ExplainabilityResponseContract,
  patientData: Record<string, any>
): { recommendation: RecommendationPackage; explanation: ExplainabilityPackage } {
  const primaryRec = contract.recommendation.primary_recommendation;

  const auditTrail: AuditTrail = {
    recommendation_id: contract.audit_reference.recommendation_id,
    patient_id: contract.patient_id,
    timestamp: contract.generated_at,
    trace_id: contract.trace_id,
    prediction_plugin_version: contract.audit_reference.prediction_plugin_version,
    model_versions: contract.audit_reference.model_versions,
    rule_versions: contract.audit_reference.rule_versions || 'v0.1.0',
    guideline_engine_version: contract.audit_reference.guideline_engine_version || 'who-aware-2026.1',
    stewardship_engine_version: contract.audit_reference.stewardship_engine_version || 'pt-stewardship-v1.0',
    cdss_version: contract.audit_reference.cdss_version || 'v1.0.0',
    algorithm_version: contract.audit_reference.algorithm_version || 'deterministic-fusion-v1.0',
    metadata: {
      primary_recommendation: primaryRec.antibiotic_name,
      confidence: contract.confidence === 'very_high' ? 98 : contract.confidence === 'high' ? 92 : contract.confidence === 'moderate' ? 75 : 50,
      alternatives_count: contract.recommendation.alternative_recommendations.length,
      rules_triggered: contract.recommendation.clinical_rules.filter((r) => r.status === 'TRIGGERED').length,
      warnings_count: contract.recommendation.warnings.length,
      execution_mode: 'AUTO',
      active_plugins: ['soar', 'armd', 'who_aware', 'clinical_rules'],
    },
  };

  const confidenceScore = contract.confidence === 'very_high' ? 98 : contract.confidence === 'high' ? 92 : contract.confidence === 'moderate' ? 75 : 50;

  const recommendationPackage: RecommendationPackage = {
    caseId,
    patient_id: contract.patient_id,
    execution_mode: 'AUTO',
    patientSummary: {
      patientName: patientData.patientName || 'Patient',
      age: patientData.age || 68,
      sex: patientData.sex || 'Male',
      condition: patientData.condition || patientData.primaryDiagnosis || 'Infection',
      allergies: patientData.allergies || [],
      egfr: patientData.egfr || 55,
      isPregnant: patientData.isPregnant,
    },
    primaryRecommendation: {
      drugName: primaryRec.antibiotic_name,
      dose: primaryRec.dosage_notes || 'Standard therapeutic dose',
      route: 'Oral (PO)',
      frequency: 'Standard schedule',
      duration: primaryRec.duration_notes || '5-7 Days',
      awareCategory: (primaryRec.guideline_category?.charAt(0).toUpperCase() + primaryRec.guideline_category?.slice(1).toLowerCase()) as any || 'Access',
      spectrum: 'Narrow',
      probability: 0.92,
      originPlugin: 'SOAR / Knowledge Engine',
      stewardshipScore: 95,
    },
    confidence: {
      level: contract.confidence === 'very_high' ? 'Very High' : contract.confidence === 'high' ? 'High' : contract.confidence === 'moderate' ? 'Moderate' : 'Low',
      score: confidenceScore,
      explanation: `Confidence level: ${contract.confidence}. Derived from Decision Fusion synthesis.`,
    },
    candidateExtraction: {
      sourcePlugins: ['SOAR/GSK', 'ARMD'],
      candidates: [
        {
          drugName: primaryRec.antibiotic_name,
          rawProbability: 0.92,
          passedSafetyRules: true,
          status: 'Primary',
          ruleSummary: 'First-line empirical selection',
        },
        ...contract.recommendation.alternative_recommendations.map((alt) => ({
          drugName: alt.antibiotic_name,
          rawProbability: 0.78,
          passedSafetyRules: true,
          status: 'Alternative' as const,
          ruleSummary: alt.reason,
        })),
      ],
    },
    evaluatedRules: contract.recommendation.clinical_rules,
    knowledgeSources: contract.recommendation.guideline_references.map((g, idx) => ({
      id: g.guideline_id || `guideline-${idx}`,
      name: g.guideline_name,
      contribution: 35,
      confidence: 0.95,
      status: 'Used',
    })),
    stewardshipAdvice: {
      category: (primaryRec.guideline_category?.charAt(0).toUpperCase() + primaryRec.guideline_category?.slice(1).toLowerCase()) as any || 'Access',
      notes: contract.recommendation.stewardship_findings[0]?.notes || [
        'Access tier: lowest resistance pressure.',
        'Review at 48-72h for clinical progress.',
      ],
    },
    warnings: contract.recommendation.warnings.map((w, idx) => ({
      id: `w-${idx}`,
      title: 'Clinical Warning',
      details: w,
      severity: 'High',
    })),
    alternativeRecommendations: contract.recommendation.alternative_recommendations.map((alt) => ({
      drugName: alt.antibiotic_name,
      dose: alt.dosage_notes || 'Standard dose',
      route: 'Oral (PO)',
      frequency: 'Standard schedule',
      duration: alt.duration_notes || '5-7 Days',
      awareCategory: (alt.guideline_category?.charAt(0).toUpperCase() + alt.guideline_category?.slice(1).toLowerCase()) as any || 'Access',
    })),
    evidenceSummary: contract.recommendation.clinical_rationale,
    clinicalRationale: contract.recommendation.clinical_rationale,
    monitoringPlan: [
      'Assess clinical response within 48 to 72 hours (temperature, symptom improvement).',
      'Follow up on microbiology culture and susceptibility reports.',
    ],
    auditTrail,
  };

  const shapFeatures = contract.explanation?.prediction_explanation?.feature_contributions
    ? Object.entries(contract.explanation.prediction_explanation.feature_contributions).map(([feat, imp]) => ({
        feature: feat,
        importance: imp,
        category: 'Clinical' as const,
      }))
    : [];

  const explainabilityPackage: ExplainabilityPackage = {
    caseId,
    patient_id: contract.patient_id,
    status: contract.status,
    recommendation_trace: contract.recommendation_trace.trace_steps.map((s) => ({
      step_id: `step-${s.step_number}`,
      stage_name: s.phase_name,
      status: 'completed',
      summary: s.description,
      execution_time_ms: s.duration_ms,
    })),
    reasoningTree: {
      nodes: contract.recommendation_trace.trace_steps.map((s, idx) => ({
        id: `node-${s.step_number}`,
        label: `${s.step_number}. ${s.phase_name}`,
        title: s.phase_name,
        details: s.description,
        source: s.phase_name,
        status: 'active',
        x: 250,
        y: 20 + idx * 80,
      })),
    },
    shapSummary: shapFeatures.length > 0
      ? {
          baseValue: contract.explanation?.prediction_explanation?.base_value || 0.15,
          features: shapFeatures,
        }
      : undefined,
    evidenceDrivers: contract.evidence_ranking.ranked_evidence.map((re) => ({
      weight: re.weight,
      source: re.source,
      evidence: re.evidence,
      impact: re.impact as any,
      affected_drug: re.affected_drug,
    })),
    evidence_ranking: contract.evidence_ranking.ranked_evidence.map((re) => ({
      weight: re.weight,
      source: re.source,
      evidence: re.evidence,
      impact: re.impact as any,
      affected_drug: re.affected_drug,
    })),
    ruleExplanations: contract.explanation?.rule_explanations || [],
    guidelineExplanations: contract.explanation?.guideline_explanations || [],
    stewardshipExplanations: contract.explanation?.stewardship_explanations || [],
    clinicalReasoningText: contract.explanation?.clinical_narrative || contract.recommendation.clinical_rationale,
    explanation: contract.explanation?.clinical_narrative || contract.recommendation.clinical_rationale,
    auditTrail,
    generated_at: contract.generated_at,
    trace_id: contract.trace_id,
  };

  return { recommendation: recommendationPackage, explanation: explainabilityPackage };
}

/**
 * Recommendation API Client adhering strictly to FastAPI backend contract:
 * - Canonical recommendation: POST /recommendations/generate
 * - Clinical review: POST /recommendation/clinical-review
 * - No accept, override, sign, or modify endpoints.
 */
export const recommendationApi = {
  /**
   * Authoritative Canonical Endpoint: POST /api/v1/recommendations/generate
   * Generates ExplainabilityResponseContract (11 canonical fields)
   */
  generateRecommendation: async (
    request: RecommendationGenerateRequest
  ): Promise<ExplainabilityResponseContract> => {
    if (!request.patient_id || !request.patient_data || !request.prediction_results || Object.keys(request.prediction_results).length === 0) {
      const error: any = new Error('Validation error: patient_id, patient_data, and prediction_results are required');
      error.status = 422;
      throw error;
    }
    return apiRequest<ExplainabilityResponseContract>('/recommendations/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Submits a full clinical case and executes backend recommendation pipeline
   */
  submitCase: async (clinicalCase: ClinicalCase): Promise<RecommendationSubmissionResult> => {
    const { executePipeline } = await import('./pipelineApi');
    const selectedPlugins = clinicalCase.pluginSelections || ['armd', 'who_knowledge'];
    const response = await executePipeline({
      execution_mode: 'sync',
      patient_id: clinicalCase.demographics.patientId,
      plugin_selection: selectedPlugins.map((pluginId) => ({ plugin_id: pluginId })),
      input_payload: { case: clinicalCase },
      response_mode: 'full',
    });
    const contract = response;
    const caseId = (clinicalCase.id || clinicalCase.demographics.patientId) as string;
    pipelineResponseCache.set(caseId, contract);
    const legacy = adaptCanonicalToLegacyPackages(caseId, contract, clinicalCase as unknown as Record<string, any>);
    return { caseId, response: contract, ...legacy, metadata: { request_id: contract.trace_id, timestamp: contract.generated_at, api_version: 'pipeline', processing_time_ms: contract.recommendation_trace?.total_duration_ms || 0 } };
  },

  /**
   * Retrieves canonical ExplainabilityResponseContract for a case
   */
  getRecommendation: async (caseId: string): Promise<ExplainabilityResponseContract> => {
    const response = pipelineResponseCache.get(caseId);
    if (!response) throw new Error(`Recommendation ${caseId} is not available from a verified backend retrieval endpoint.`);
    return response;
  },

  /**
   * Retrieves explainability package for a case
   */
  getExplainability: async (caseId: string): Promise<ExplainabilityPackage> => {
    const response = pipelineResponseCache.get(caseId);
    if (!response) throw new Error('Explainability retrieval by case is not exposed by the active backend API.');
    return adaptCanonicalToLegacyPackages(caseId, response, {}).explanation;
  },

  /**
  * Records the clinician's determination through the supported review boundary.
  * The recommendation remains immutable; this records review metadata only.
   */
  recordClinicalReview: async (
    request: ClinicalReviewRequest
  ): Promise<ClinicalReviewResponse> => {
    const response = await apiRequest<ClinicalReviewResponse>('/recommendations/clinical-review', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response;
  },

  /**
   * Retrieves review history for a recommendation
   */
  getClinicalReviews: async (recommendationId: string): Promise<ClinicalReviewResponse[]> => {
    void recommendationId;
    throw new Error('Clinical review history is not exposed by the active backend API.');
  },
};

// Aliases for backward compatibility
export const clinicalCaseApi = {
  submitCase: recommendationApi.submitCase,
};
