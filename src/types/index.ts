export * from './auth';
import { UserRole } from './auth';

// ----------------------------------------------------
// Backend Architecture Baseline v1.0 Contracts
// ----------------------------------------------------

export type PluginType = 'PREDICTION' | 'KNOWLEDGE' | 'RISK' | 'RULES' | 'REPORTING' | 'INTEGRATION';

export type ExecutionMode = 
  | 'AUTO' 
  | 'HYBRID' 
  | 'PREDICTION_ONLY' 
  | 'KNOWLEDGE_ONLY' 
  | 'USER_SELECTED' 
  | 'WORKFLOW_SELECTED';

export interface PluginInfo {
  id: string;
  name: string;
  type: PluginType;
  version: string;
  description: string;
  author: string;
  status: 'Active' | 'Inactive' | 'Degraded';
  executionTimeMs?: number;
  capabilities: string[];
}

export interface PredictionResult {
  predicted_class: string;
  probabilities: Record<string, number>; // Candidate antibiotics originate exclusively from here
  confidence: number;
  model_name: string;
  model_version: string;
  execution_time_ms: number;
  metadata?: Record<string, any>;
  raw_output?: Record<string, any>;
}

export interface KnowledgeResultItem {
  guideline_id: string;
  guideline_name: string;
  category: 'Access' | 'Watch' | 'Reserve';
  evidence_level: 'A-I' | 'B-II' | 'C-III';
  drug_name: string;
  recommendations: string;
  contraindications: string[];
  metadata?: Record<string, any>;
}

export interface ClinicalRuleResult {
  rule_id: string;
  rule_name: 'Allergy' | 'Renal Impairment' | 'Pregnancy' | 'Lactation' | 'Drug Interaction' | string;
  status: 'PASSED' | 'TRIGGERED' | 'WARNING' | string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | string;
  affected_drugs: string[];
  message: string;
  dosage_notes?: string;
  adjustment_notes?: string; // Legacy fallback
}

export interface ExplainabilityDriver {
  weight: number; // composite importance 0 - 1
  source: 'Prediction Engine' | 'Clinical Rules' | 'WHO Guidelines' | 'Stewardship Policy' | 'Regional Surveillance' | string;
  evidence: string;
  impact: 'Supports' | 'Restricts' | 'Caution' | 'Contraindicates' | 'Positive' | 'Negative' | string;
  affected_drug?: string;
  confidence?: number;
  clinical_importance?: number;
}

// ----------------------------------------------------
// Phase 9 Canonical Backend Contracts (Verified by Backend Truth & OpenAPI Registry)
// ----------------------------------------------------

export type ConfidenceLevel = 'very_high' | 'high' | 'moderate' | 'low' | 'very_low';

export interface PrimaryRecommendation {
  antibiotic_name: string;
  reason: string;
  guideline_category: 'access' | 'watch' | 'reserve' | 'Access' | 'Watch' | 'Reserve' | string;
  ranking: number;
  confidence: ConfidenceLevel;
  alternative: boolean;
  warnings: string[];
  dosage_notes?: string;
  duration_notes?: string;
}

export interface AlternativeRecommendation {
  antibiotic_name: string;
  reason: string;
  guideline_category: 'access' | 'watch' | 'reserve' | 'Access' | 'Watch' | 'Reserve' | string;
  ranking: number;
  confidence: ConfidenceLevel;
  alternative: boolean;
  warnings: string[];
  dosage_notes?: string;
  duration_notes?: string;
}

export interface GuidelineReference {
  guideline_id?: string;
  guideline_name: string;
  category?: string;
  evidence_level?: string;
  drug_name?: string;
  recommendations?: string;
  contraindications?: string[];
  url?: string;
}

export interface StewardshipFinding {
  finding_id?: string;
  title?: string;
  category: 'access' | 'watch' | 'reserve' | 'Access' | 'Watch' | 'Reserve' | string;
  score?: number;
  finding?: string;
  recommendation?: string;
  rationale?: string;
  notes?: string[];
}

export interface RecommendationResult {
  patient_id: string;
  primary_recommendation: PrimaryRecommendation;
  alternative_recommendations: AlternativeRecommendation[];
  clinical_rules: ClinicalRuleResult[];
  guideline_references: GuidelineReference[];
  stewardship_findings: StewardshipFinding[];
  warnings: string[];
  clinical_rationale: string;
  confidence: ConfidenceLevel;
  supporting_evidence: string[];
  generated_at: string;
  version: string;
}

export interface RankedEvidence {
  weight: number; // composite weight (confidence * clinical_importance)
  source: string;
  evidence: string;
  impact: 'Supports' | 'Restricts' | 'Caution' | 'Contraindicates' | 'Positive' | 'Negative' | string;
  affected_drug?: string;
  confidence?: number;
  clinical_importance?: number;
}

export interface EvidenceRanking {
  recommendation_id: string;
  patient_id: string;
  ranked_evidence: RankedEvidence[];
  ranking_algorithm: string;
  timestamp: string;
}

export interface EvidenceAttribution {
  source?: string;
  plugin_name?: string;
  evidence_type?: string;
  contribution_score?: number;
  details?: string;
  timestamp?: string;
  metadata?: Record<string, any>;
}

export interface RecommendationTraceStep {
  step_number: number;
  phase_name: string;
  description: string;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  duration_ms: number;
  timestamp: string;
}

export interface RecommendationTrace {
  recommendation_id: string;
  patient_id: string;
  trace_steps: RecommendationTraceStep[];
  total_duration_ms: number;
  timestamp: string;
}

export interface AuditReference {
  recommendation_id: string;
  patient_id: string;
  timestamp: string;
  trace_id: string;
  prediction_plugin_version: string;
  model_versions: Record<string, string>;
  rule_versions?: string;
  guideline_engine_version?: string;
  stewardship_engine_version?: string;
  cdss_version?: string;
  algorithm_version?: string;
  metadata?: Record<string, any>;
}

export interface PredictionExplanation {
  feature_contributions?: Record<string, number>;
  feature_importance?: Record<string, number>;
  shap_values?: Record<string, number>;
  method?: string;
  base_value?: number;
}

export interface RecommendationExplanation {
  recommendation_id: string;
  patient_id: string;
  primary_antibiotic: string;
  prediction_explanation?: PredictionExplanation | null;
  rule_explanations: string[];
  guideline_explanations: string[];
  stewardship_explanations: string[];
  evidence_drivers: RankedEvidence[];
  warnings: string[];
  clinical_narrative: string;
  generated_at: string;
}

export interface ExplainabilityResponseContract {
  status: 'success' | 'error'; // Strictly "success" | "error" (warning is NOT a top-level status)
  patient_id: string;
  recommendation: RecommendationResult;
  confidence: ConfidenceLevel; // string: "very_high" | "high" | "moderate" | "low" | "very_low"
  evidence_ranking: EvidenceRanking;
  evidence_attribution: EvidenceAttribution[]; // default []
  recommendation_trace: RecommendationTrace;
  audit_reference: AuditReference;
  explanation: RecommendationExplanation | null; // OPTIONAL (can be null)
  generated_at: string; // ISO 8601 string
  trace_id: string; // distributed trace UUID
}

export interface ClinicalReviewRequest {
  recommendation_id: string;
  clinician_id: string;
  review_decision: 'APPROVED' | 'MODIFIED' | 'REJECTED';
  selected_antibiotic?: string;
  clinical_notes?: string;
  reason_for_deviation?: string;
}

export interface ClinicalReviewResponse {
  status: string;
  recommendation_id: string;
  review_decision: 'APPROVED' | 'MODIFIED' | 'REJECTED' | string;
  clinician_id: string;
  recorded_at: string;
  message: string;
  selected_antibiotic?: string;
  clinical_notes?: string;
  reason_for_deviation?: string;
}

export interface RecommendationGenerateRequest {
  patient_id: string;
  patient_data: Record<string, any>;
  prediction_results: Record<string, number>;
  prediction_explanation?: Record<string, any>;
  prediction_plugin_version?: string;
  model_versions?: Record<string, string>;
}

export interface AuditTrail {
  recommendation_id: string;
  patient_id: string;
  timestamp: string;
  trace_id: string;
  prediction_plugin_version?: string;
  model_versions: Record<string, string>;
  rule_versions: string;
  guideline_engine_version: string;
  stewardship_engine_version: string;
  cdss_version: string;
  algorithm_version: string;
  metadata: {
    primary_recommendation: string;
    confidence: number;
    alternatives_count: number;
    rules_triggered: number;
    warnings_count: number;
    execution_mode: ExecutionMode;
    active_plugins: string[];
  };
}

// ----------------------------------------------------
// Dashboard Types
// ----------------------------------------------------
export interface DashboardStat {
  title: string;
  value: string;
  change?: string;
  changeType?: 'increase' | 'decrease';
  iconName: string;
}

export interface ChartDataPoint {
  name: string;
  value: number;
}

export interface RecentActivityItem {
  id: string;
  patientName: string;
  activity: string;
  timestamp: string;
  status: 'Completed' | 'Pending' | 'Alert';
}

export interface DashboardData {
  stats: DashboardStat[];
  confidenceDistribution: ChartDataPoint[];
  diseaseDistribution: ChartDataPoint[];
  recentActivity: RecentActivityItem[];
}

// ----------------------------------------------------
// Clinical Case Assessment Types
// ----------------------------------------------------
export interface Demographics {
  patientId?: string;
  patientName?: string;
  age: number;
  sex: 'Male' | 'Female' | 'Other';
  weight?: number;
  creatinineClearance?: number;
}

export interface Presentation {
  symptoms: string[];
  primaryDiagnosis: string;
  infectionSite: string;
  severity: 'Non-severe' | 'Moderate' | 'Severe' | 'Critical/Sepsis';
  vitals: {
    temperature?: number;
    heartRate?: number;
    respiratoryRate?: number;
    bloodPressure?: string;
    oxygenSaturation?: number;
  };
}

export interface Laboratory {
  crp?: number;
  wbc?: number;
  creatinine?: number;
  procalcitonin?: number;
  egfr?: number;
  cultureResult?: string;
  gramStain?: string;
  suspectedPathogen?: string;
}

export interface RiskFactors {
  allergies: string[];
  comorbidities: string[];
  concomitantMedications?: string[];
  isPregnant: boolean;
  isLactating?: boolean;
  isImmunocompromised: boolean;
  priorAntibiotics90Days: boolean;
  recentHospitalization: boolean;
}

export interface ClinicalCase {
  id?: string;
  demographics: Demographics;
  presentation: Presentation;
  laboratory: Laboratory;
  riskFactors: RiskFactors;
  executionMode?: ExecutionMode;
  pluginSelections?: string[];
  status?: 'Draft' | 'Submitted' | 'Analyzed';
  createdAt?: string;
}

// ----------------------------------------------------
// Recommendation Package Types (Backend Standard Envelope)
// ----------------------------------------------------
export interface DrugRecommendation {
  drugName: string;
  dose: string;
  route: string;
  frequency: string;
  duration: string;
  awareCategory: 'Access' | 'Watch' | 'Reserve';
  costTier?: 'Low' | 'Moderate' | 'High';
  spectrum?: 'Narrow' | 'Broad' | 'Extended';
  probability?: number;
  originPlugin?: string;
  stewardshipScore?: number;
}

export interface KnowledgeSource {
  id: string;
  name: string;
  contribution: number; // percentage 0-100
  confidence: number;   // 0 to 1
  status: 'Used' | 'Consulted' | 'Unavailable';
  lastUpdated?: string;
}

export interface ClinicalWarning {
  id: string;
  title: string;
  details: string;
  severity: 'High' | 'Medium' | 'Low';
  ruleSource?: string;
}

export interface RecommendationPackage {
  caseId: string;
  patient_id?: string;
  execution_mode?: ExecutionMode;
  patientSummary: {
    patientName: string;
    age: number;
    sex: string;
    condition: string;
    allergies: string[];
    egfr?: number;
    isPregnant?: boolean;
  };
  primaryRecommendation: DrugRecommendation;
  confidence: {
    level: 'Very High' | 'High' | 'Moderate' | 'Low';
    score: number; // 0 - 100
    explanation: string;
  };
  candidateExtraction: {
    sourcePlugins: string[];
    candidates: {
      drugName: string;
      rawProbability: number;
      passedSafetyRules: boolean;
      status: 'Primary' | 'Alternative' | 'Contraindicated' | 'Adjusted';
      ruleSummary?: string;
    }[];
  };
  evaluatedRules: ClinicalRuleResult[];
  knowledgeSources: KnowledgeSource[];
  stewardshipAdvice: {
    category: 'Access' | 'Watch' | 'Reserve';
    notes: string[];
  };
  warnings: ClinicalWarning[];
  alternativeRecommendations: DrugRecommendation[];
  evidenceSummary: string;
  clinicalRationale: string;
  monitoringPlan: string[];
  auditTrail: AuditTrail;
  acceptedByClinician?: boolean;
  clinicianOverride?: {
    overridden: boolean;
    selectedDrug?: string;
    reason?: string;
    clinicianName?: string;
    timestamp?: string;
  };
}

// ----------------------------------------------------
// Explainability Package Types
// ----------------------------------------------------
export interface ShapFeature {
  feature: string;
  importance: number; // positive or negative
  category?: 'Demographics' | 'Clinical' | 'Lab' | 'Surveillance' | 'Rule' | 'General';
}

export interface ReasoningNode {
  id: string;
  label: string;
  title: string;
  details: string;
  source?: 'Patient Data' | 'Workflow Manager' | 'Prediction Plugin' | 'Rules Engine' | 'Decision Fusion' | 'Explainability' | 'WHO' | 'SOAR' | 'ARMD' | 'Output' | string;
  confidence?: string;
  status?: 'active' | 'passive' | string;
  x?: number;
  y?: number;
}

export interface ReasoningEdge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
  label?: string;
}

export interface TraceStep {
  step_id: string;
  stage_name: string;
  status: string;
  summary: string;
  execution_time_ms?: number;
}

export interface ExplainabilityPackage {
  caseId: string;
  patient_id?: string;
  status?: string;
  reasoningTree?: {
    nodes: ReasoningNode[];
    edges?: ReasoningEdge[];
  };
  recommendation_trace?: TraceStep[];
  shapSummary?: {
    baseValue?: number;
    features: ShapFeature[];
  };
  evidenceDrivers?: ExplainabilityDriver[];
  evidence_ranking?: ExplainabilityDriver[];
  ruleExplanations?: string[];
  guidelineExplanations?: string[];
  stewardshipExplanations?: string[];
  confidenceBreakdown?: {
    title: string;
    details: string;
    score: number;
  }[];
  clinicalReasoningText?: string;
  explanation?: string;
  auditTrail: AuditTrail;
  generated_at?: string;
  trace_id?: string;
}

// ----------------------------------------------------
// WHO Knowledge Explorer Types
// ----------------------------------------------------
export interface DiseaseSummary {
  id: string;
  name: string;
  category: string;
  commonPathogens: string[];
  awareClass: 'Access' | 'Watch' | 'Reserve';
}

export interface AntimicrobialRecommendation {
  id: string;
  context: 'Adult' | 'Child' | 'Severe' | 'Non-severe';
  drug: string;
  dose: string;
  route: string;
  frequency: string;
  duration: string;
  evidenceGrade: 'A-I' | 'B-II' | 'C-III';
}

export interface DiseaseDetail extends DiseaseSummary {
  overview: string;
  recommendations: AntimicrobialRecommendation[];
  diagnostics: string[];
  monitoring: string[];
  stewardship: string[];
  referralCriteria: string[];
}

// ----------------------------------------------------
// SOAR Explorer Types
// ----------------------------------------------------
export interface SoarDataPoint {
  id: string;
  country: string;
  year: number;
  pathogen: 'Streptococcus pneumoniae' | 'Haemophilus influenzae' | 'Escherichia coli' | 'Klebsiella pneumoniae' | 'Pseudomonas aeruginosa' | 'Staphylococcus aureus';
  antibiotic: 'Amoxicillin' | 'Azithromycin' | 'Cefuroxime' | 'Ciprofloxacin' | 'Co-amoxiclav' | 'Levofloxacin' | 'Nitrofurantoin';
  resistancePercent: number;
  susceptiblePercent: number;
  intermediatePercent: number;
  sampleSize: number;
}

// ----------------------------------------------------
// ARMD Explorer Types
// ----------------------------------------------------
export interface ArmdModelSummary {
  id: string;
  name: string;
  description: string;
  targetPathogen: string;
  targetDrug: string;
}

export interface PerformanceMetrics {
  aucRoc: number;
  precision: number;
  recall: number;
  f1Score: number;
}

export interface MicDistributionPoint {
  mic: number;
  susceptibleCount: number;
  resistantCount: number;
}

export interface ArmdModelDetail {
  id: string;
  name: string;
  targetPathogen: string;
  targetDrug: string;
  performanceMetrics: PerformanceMetrics;
  featureImportance: ShapFeature[];
  micDistribution: MicDistributionPoint[];
  lastTrained: string;
  datasetSize: number;
}

// ----------------------------------------------------
// Patient History & Audit Types
// ----------------------------------------------------
export interface PatientSummary {
  id: string;
  name: string;
  dateOfBirth: string;
  gender: string;
  lastActivity: string;
  recordCount: number;
}

export interface PatientDetails {
  id: string;
  name: string;
  age: number;
  sex: string;
  allergies: string[];
  comorbidities: string[];
  mrn: string;
}

export interface HistoryEvent {
  id: string;
  type: 'Assessment' | 'Recommendation' | 'Stewardship Alert' | 'Clinician Action' | 'Lab Result' | 'Clinical Override';
  timestamp: string;
  user: string;
  summary: string;
  payload: Record<string, any>;
}

// ----------------------------------------------------
// Admin & Governance Types
// ----------------------------------------------------
export type SystemStatus = 'Operational' | 'Degraded' | 'Offline';

export interface SystemComponent {
  name: string;
  status: SystemStatus;
  details: string;
  latencyMs?: number;
  uptimePercent?: number;
  slaTarget?: number;
  lastChecked?: string;
}

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: 'Active' | 'Inactive';
  lastLogin: string;
  department: string;
  licenseNumber?: string;
  assessmentsCount?: number;
}

export interface KnowledgeSourceStatus {
  name: string;
  status: SystemStatus;
  version: string;
  lastUpdated: string;
  recordCount: number;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  details: string;
  severity: 'Info' | 'Warning' | 'Critical';
  traceId?: string;
  category?: 'CLINICAL' | 'AUTH' | 'GOVERNANCE' | 'SYSTEM' | 'SECURITY';
  payload?: Record<string, any>;
}

export interface StewardshipPolicy {
  id: string;
  title: string;
  description: string;
  category: 'AWaRe' | 'Formulary' | 'Pre-Authorization' | 'Duration' | 'Dosing';
  targetMetric: string;
  currentValue: string | number;
  targetValue: string | number;
  status: 'Compliant' | 'Warning' | 'Action Required';
  restrictionLevel: 'Open' | 'Restricted' | 'Pre-Authorization Required';
  affectedAntibiotics: string[];
  lastReviewed: string;
  rationale?: string;
}

export interface GovernanceMetric {
  title: string;
  value: string | number;
  target?: string | number;
  status: 'Optimal' | 'Warning' | 'Attention';
  change?: string;
  description: string;
}

export interface AuditFilterOptions {
  query?: string;
  severity?: 'All' | 'Info' | 'Warning' | 'Critical';
  category?: string;
  startDate?: string;
  endDate?: string;
}

export interface AdminDashboardData {
  systemHealth: SystemComponent[];
  plugins: PluginInfo[];
  users: AdminUser[];
  knowledgeSourceStatus: KnowledgeSourceStatus[];
  auditTrail: AuditEvent[];
  stewardshipPolicies?: StewardshipPolicy[];
  governanceMetrics?: GovernanceMetric[];
}

// ----------------------------------------------------
// User Settings
// ----------------------------------------------------
export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  defaultDosingUnit: 'mg' | 'g' | 'mg/kg';
  awareStrictMode: boolean;
  highRiskAlertThreshold: number; // percentage
  defaultExecutionMode: ExecutionMode;
  emailNotifications: boolean;
  autoSaveDrafts: boolean;
}
