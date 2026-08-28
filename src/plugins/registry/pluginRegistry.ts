/**
 * Phase 11: Plugin Registry & Telemetry Extractors
 * Central abstraction for querying registered plugins and extracting telemetry from canonical responses.
 */

import { ExplainabilityResponseContract, EvidenceAttribution, AuditReference } from '@/types';
import { CANONICAL_PLUGINS } from './pluginDefinitions';
import {
  PluginDefinition,
  PluginCategory,
  PluginContribution,
  RecommendationTelemetry,
} from './pluginTypes';

/**
 * Returns all registered plugins defined in the frontend registry.
 */
export function getRegisteredPlugins(): PluginDefinition[] {
  return [...CANONICAL_PLUGINS];
}

/**
 * Finds a plugin definition by its ID or canonical alias.
 */
export function getPluginById(id: string): PluginDefinition | undefined {
  const normId = id.toLowerCase().trim();
  return CANONICAL_PLUGINS.find(
    (p) =>
      p.id.toLowerCase() === normId ||
      p.name.toLowerCase().includes(normId) ||
      normId.includes(p.id.toLowerCase())
  );
}

/**
 * Filters registered plugins by category.
 */
export function getPluginsByCategory(category: PluginCategory): PluginDefinition[] {
  return CANONICAL_PLUGINS.filter((p) => p.category === category);
}

/**
 * Backend capability truth: only 'knowledge' and 'prediction' category
 * components are genuinely registered/pluggable capabilities (WHO AWaRe,
 * SOAR, ARMD). Clinical Rules, Decision Fusion, Explainability, and
 * Audit & Telemetry are inbuilt platform architecture — never registered
 * plugins — and must never be presented as such in the UI.
 */
const REGISTERED_PLUGIN_CATEGORIES: PluginCategory[] = ['knowledge', 'prediction'];

export function isRegisteredPluginCategory(category: PluginCategory): boolean {
  return REGISTERED_PLUGIN_CATEGORIES.includes(category);
}

export function getExternalRegisteredPlugins(): PluginDefinition[] {
  return CANONICAL_PLUGINS.filter((p) => isRegisteredPluginCategory(p.category));
}

export function getInbuiltPlatformComponents(): PluginDefinition[] {
  return CANONICAL_PLUGINS.filter((p) => !isRegisteredPluginCategory(p.category));
}

/**
 * Maps evidence attribution items returned from the backend's canonical response
 * to structured PluginContribution objects.
 *
 * ONLY maps data that is actually present. If attribution is empty or absent, returns an empty array.
 */
export function mapEvidenceAttributionsToContributions(
  attributions?: EvidenceAttribution[] | null
): PluginContribution[] {
  if (!attributions || !Array.isArray(attributions) || attributions.length === 0) {
    return [];
  }

  return attributions.map((attr) => {
    const sourceName = attr.source || attr.plugin_name || 'Unknown Source';
    const matchedPlugin = getPluginById(sourceName);

    let contributionType: PluginContribution['contributionType'] = 'evidence';
    const evidenceType = (attr.evidence_type || '').toLowerCase();
    if (evidenceType.includes('predict') || sourceName.toLowerCase().includes('predict') || sourceName.toLowerCase().includes('soar') || sourceName.toLowerCase().includes('armd')) {
      contributionType = 'prediction';
    } else if (evidenceType.includes('rule') || sourceName.toLowerCase().includes('rule') || sourceName.toLowerCase().includes('safety')) {
      contributionType = 'rule';
    } else if (evidenceType.includes('fusion') || sourceName.toLowerCase().includes('fusion')) {
      contributionType = 'fusion';
    } else if (evidenceType.includes('explain') || sourceName.toLowerCase().includes('explain') || evidenceType.includes('shap')) {
      contributionType = 'explanation';
    }

    return {
      pluginId: matchedPlugin ? matchedPlugin.id : sourceName.toLowerCase().replace(/\s+/g, '_'),
      pluginName: matchedPlugin ? matchedPlugin.name : sourceName,
      category: matchedPlugin?.category,
      contributionType,
      source: attr.source || matchedPlugin?.source,
      weight: typeof attr.contribution_score === 'number' ? attr.contribution_score : undefined,
      attribution: attr,
      details: attr.details,
      timestamp: attr.timestamp,
    };
  });
}

/**
 * Extracts pure, verified telemetry from the canonical ExplainabilityResponseContract.
 * Does NOT invent or synthesize missing fields.
 */
export function extractTelemetryFromContract(
  contract?: ExplainabilityResponseContract | null
): RecommendationTelemetry | null {
  if (!contract) return null;

  const pluginContributions = mapEvidenceAttributionsToContributions(contract.evidence_attribution);

  const audit = contract.audit_reference;

  return {
    traceId: contract.trace_id,
    generatedAt: contract.generated_at,
    auditReference: audit as unknown as Record<string, unknown>,
    confidence: contract.confidence,
    recommendationId: audit?.recommendation_id,
    pluginContributions,
    predictionPluginVersion: audit?.prediction_plugin_version,
    modelVersions: audit?.model_versions,
    ruleVersions: audit?.rule_versions,
    guidelineEngineVersion: audit?.guideline_engine_version,
    stewardshipEngineVersion: audit?.stewardship_engine_version,
    cdssVersion: audit?.cdss_version,
    algorithmVersion: audit?.algorithm_version,
    totalDurationMs: contract.recommendation_trace?.total_duration_ms,
    traceStepsCount: contract.recommendation_trace?.trace_steps?.length,
  };
}
