from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence


class RecommendationRanker:
    """Ranks candidate antibiotics using probability and rule-derived constraints."""

    def rank(self, prediction_results: Dict[str, float], clinical_rule_results: Sequence[Any] | None = None) -> List[tuple[str, float]]:
        contraindicated = set()
        for rule in clinical_rule_results or []:
            status = getattr(rule, "status", None)
            if str(status) == "RuleStatus.TRIGGERED" or str(status) == "triggered":
                for drug in getattr(rule, "affected_drugs", []) or []:
                    contraindicated.add(drug)

        ranked = []
        for antibiotic, probability in prediction_results.items():
            if antibiotic in contraindicated:
                continue
            ranked.append((antibiotic, float(probability)))
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked
