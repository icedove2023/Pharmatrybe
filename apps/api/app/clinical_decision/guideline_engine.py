"""Guideline Engine for retrieving clinical evidence.

Initially uses placeholder data. Will be extended to integrate:
- WHO AWaRe
- NICE guidelines
- IDSA guidelines
- Local hospital policies
"""

from typing import Any, Dict, List, Optional
import logging

from .contracts import GuidelineReference, GuidelineCategory

logger = logging.getLogger(__name__)


class GuidelineEngine:
    """Engine for retrieving clinical guideline evidence.
    
    Responsible for sourcing guideline data and making it available
    to the decision fusion engine.
    
    Initially uses placeholder data.
    """

    def __init__(self):
        """Initialize guideline engine with placeholder guidelines."""
        self.guidelines: Dict[str, GuidelineReference] = {}
        self.logger = logging.getLogger(__name__)
        self._load_placeholder_guidelines()

    def _load_placeholder_guidelines(self) -> None:
        """Load placeholder guidelines for demonstration.
        
        In production, this would query a knowledge base or guideline API.
        """
        # Placeholder: WHO AWaRe Access antibiotics (first-line)
        access_antibiotics = [
            "amoxicillin",
            "ampicillin",
            "penicillin",
            "cephalexin",
            "ceftriaxone",
            "gentamicin",
            "trimethoprim-sulfamethoxazole",
        ]
        
        for ab in access_antibiotics:
            self.guidelines[f"who_aware_{ab}"] = GuidelineReference(
                guideline_id=f"who_aware_{ab}",
                guideline_name=f"WHO AWaRe: {ab.title()}",
                category=GuidelineCategory.ACCESS,
                recommendation=f"{ab.title()} is a WHO Access antibiotic suitable for first-line therapy",
                source="WHO",
                url="https://www.who.int/publications/i/item/WHO-EMP-IAU-2019.11",
            )
        
        # Placeholder: WHO AWaRe Watch antibiotics (reserve use)
        watch_antibiotics = [
            "ciprofloxacin",
            "levofloxacin",
            "azithromycin",
            "ceftazidime",
        ]
        
        for ab in watch_antibiotics:
            self.guidelines[f"who_aware_{ab}"] = GuidelineReference(
                guideline_id=f"who_aware_{ab}",
                guideline_name=f"WHO AWaRe: {ab.title()}",
                category=GuidelineCategory.WATCH,
                recommendation=f"{ab.title()} is a WHO Watch antibiotic; reserve for specific indications",
                source="WHO",
                url="https://www.who.int/publications/i/item/WHO-EMP-IAU-2019.11",
            )
        
        self.logger.info(f"Loaded {len(self.guidelines)} placeholder guidelines")

    def get_guideline_by_antibiotic(self, antibiotic: str) -> Optional[GuidelineReference]:
        """Get guideline reference for an antibiotic.
        
        Args:
            antibiotic: Antibiotic name
            
        Returns:
            GuidelineReference or None if not found
        """
        key = f"who_aware_{antibiotic.lower()}"
        return self.guidelines.get(key)

    def get_guidelines_by_category(
        self,
        category: GuidelineCategory
    ) -> List[GuidelineReference]:
        """Get all guidelines in a category.
        
        Args:
            category: Guideline category (ACCESS, WATCH, RESERVE)
            
        Returns:
            List of GuidelineReferences in the category
        """
        return [g for g in self.guidelines.values() if g.category == category]

    def get_all_guidelines(self) -> List[GuidelineReference]:
        """Get all guidelines.
        
        Returns:
            List of all GuidelineReferences
        """
        return list(self.guidelines.values())

    def query_guidelines(self, query: str) -> List[GuidelineReference]:
        """Query guidelines by text search.
        
        Args:
            query: Search query
            
        Returns:
            Matching guidelines
        """
        query_lower = query.lower()
        results = [
            g for g in self.guidelines.values()
            if query_lower in g.guideline_name.lower()
            or query_lower in g.recommendation.lower()
            or query_lower in g.source.lower()
        ]
        return results
