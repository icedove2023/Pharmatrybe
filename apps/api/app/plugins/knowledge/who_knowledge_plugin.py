"""WHO Knowledge Plugin for PharmaTrybe.

Wraps the existing WHO SQL knowledge base inside the PharmaTrybe Knowledge
Plugin architecture, exposing WHO clinical knowledge through the standardized
plugin interface.

This plugin is read-only; it retrieves and structures WHO knowledge without
modifying the underlying database.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.base.plugin import PluginHealth, PluginMetadata, PluginType
from app.database.repositories.who_knowledge_repository import WHOKnowledgeRepository
from app.knowledge.providers.who_provider import WHOProvider
from app.knowledge.providers.query_models import KnowledgeQuery, SearchQuery
from app.database.who_connection import get_who_session


logger = logging.getLogger(__name__)


@dataclass
class WHOKnowledgeResult:
    """Structured output from WHO Knowledge Plugin."""

    source: str = "WHO"
    plugin_version: str = ""
    knowledge_version: str = ""
    
    # Search result type
    result_type: str = ""  # "disease", "drug", "recommendation", "evidence"
    
    # Entity information
    entity_id: str = ""
    entity_name: str = ""
    entity_description: str = ""
    
    # Clinical classification
    guideline_category: Optional[str] = None  # For drugs: Access/Watch/Reserve
    clinical_recommendation: str = ""
    evidence_level: str = "MEDIUM"  # HIGH/MEDIUM/LOW
    
    # Structured data
    citation: str = "WHO Guidelines"
    source_version: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "source": self.source,
            "plugin_version": self.plugin_version,
            "knowledge_version": self.knowledge_version,
            "result_type": self.result_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "entity_description": self.entity_description,
            "guideline_category": self.guideline_category,
            "clinical_recommendation": self.clinical_recommendation,
            "evidence_level": self.evidence_level,
            "citation": self.citation,
            "source_version": self.source_version,
            "metadata": self.metadata,
        }


class WHOKnowledgePlugin(KnowledgePlugin):
    """Knowledge Plugin for WHO clinical guidelines.
    
    Provides access to WHO respiratory infection guidelines through the
    PharmaTrybe Knowledge Plugin interface. Reuses existing WHO SQL database
    and repository implementation.
    
    This plugin:
    - Retrieves WHO clinical knowledge only
    - Never generates recommendations
    - Never predicts patient outcomes
    - Provides evidence for clinician review
    """

    def __init__(self, db_session: Optional[Session] = None) -> None:
        """Initialize WHO Knowledge Plugin.
        
        Args:
            db_session: SQLAlchemy session for database access
        """
        self._session = db_session or get_who_session()
        self._owns_session = db_session is None
        self._repository: Optional[WHOKnowledgeRepository] = None
        self._provider: Optional[WHOProvider] = None
        self._is_connected = False
        self._initialization_time: Optional[datetime] = None

    # ========== Properties ==========

    @property
    def plugin_id(self) -> str:
        """Unique plugin identifier."""
        return "who_knowledge"

    @property
    def plugin_name(self) -> str:
        """Human-readable plugin name."""
        return "WHO Knowledge Base"

    @property
    def plugin_version(self) -> str:
        """Plugin version (code version)."""
        return "0.1.0"

    @property
    def plugin_type(self) -> PluginType:
        """Plugin type must be KNOWLEDGE."""
        return PluginType.KNOWLEDGE

    @property
    def plugin_description(self) -> str:
        """Plugin description."""
        return "WHO respiratory infection clinical guidelines and antimicrobial stewardship evidence"

    @property
    def author(self) -> str:
        """Plugin author/owner."""
        return "WHO / PharmaTrybe Team"

    @property
    def capabilities(self) -> List[str]:
        """Capabilities exposed to the platform."""
        return [
            "disease_guidelines",
            "antibiotic_classification",
            "antimicrobial_stewardship",
            "diagnostic_guidance",
            "treatment_recommendations",
            "monitoring_guidance",
            "follow_up_guidance",
            "evidence_retrieval",
        ]

    @property
    def dependencies(self) -> List[str]:
        """Plugin dependencies."""
        return [
            "python3.9+",
            "sqlalchemy",
            "postgresql",
        ]

    # ========== Lifecycle Methods ==========

    def initialize(self) -> None:
        """Initialize plugin at startup.
        
        Sets up internal state but does not connect to database yet.
        Connection happens in connect() method.
        """
        logger.info(f"Initializing {self.plugin_name} (v{self.plugin_version})")
        self._initialization_time = datetime.now(timezone.utc)
        logger.info(f"{self.plugin_name} initialized")

    def shutdown(self) -> None:
        """Shutdown plugin at unload."""
        logger.info(f"Shutting down {self.plugin_name}")
        if self._is_connected:
            self.disconnect()
        self._repository = None
        self._provider = None
        if self._owns_session and self._session is not None:
            self._session.close()
            self._session = None
        logger.info(f"{self.plugin_name} shutdown complete")

    def configure(self, configuration: Dict[str, Any]) -> None:
        """Configure plugin with runtime parameters.
        
        Args:
            configuration: Configuration dictionary (not currently used,
                          kept for interface compliance)
        
        Raises:
            ValueError: If configuration is invalid
        """
        logger.info(f"Configuring {self.plugin_name}")
        # WHO plugin uses shared database session, no additional config needed
        logger.info(f"{self.plugin_name} configuration complete")

    def validate(self) -> bool:
        """Validate plugin readiness.
        
        Returns:
            True if plugin is ready to handle requests, False otherwise
        """
        if not self._is_connected:
            logger.warning(f"{self.plugin_name} not connected")
            return False
        
        if self._repository is None or self._provider is None:
            logger.warning(f"{self.plugin_name} components not initialized")
            return False
        
        return True

    def metadata(self) -> PluginMetadata:
        """Return structured plugin metadata."""
        return PluginMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
        )

    def health(self) -> PluginHealth:
        """Return structured health status."""
        return PluginHealth(
            healthy=self._is_connected,
            status="connected" if self._is_connected else "disconnected",
            message=None if self._is_connected else "Database connection not established",
            timestamp=datetime.now(timezone.utc),
        )

    def input_schema(self) -> Dict[str, Any]:
        """Return the WHO knowledge-query contract, not a prediction input."""
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "WHO knowledge query",
            "x-contract-kind": "knowledge_query",
            "oneOf": [
                {"title": "SearchQuery", "type": "object", "properties": {
                    "query_text": {"type": "string", "minLength": 1},
                    "entity_type": {"type": "string"},
                }, "required": ["query_text"], "additionalProperties": False},
                {"title": "KnowledgeQuery", "type": "object", "properties": {
                    "entity_type": {"type": "string"},
                    "identifier": {"type": "string"},
                }, "additionalProperties": False},
            ],
            "x-plugin-runtime-mappings": {
                "contract": "KnowledgeQuery or SearchQuery",
                "search_query": {"required": ["query_text"], "executed_fields": ["query_text", "entity_type"]},
                "knowledge_query": {"required_for_retrieval": ["entity_type"], "optional_for_lookup": ["identifier"], "executed_fields": ["entity_type", "identifier"]},
            },
        }

    def output_schema(self) -> Dict[str, Any]:
        """Return the WHO knowledge query output schema."""
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "WHO knowledge output",
            "type": "object",
            "properties": {
                "result_type": {"type": "string"},
                "entity_name": {"type": "string"},
                "clinical_recommendation": {"type": "string"},
                "evidence_level": {"type": "string"},
                "citation": {"type": "string"},
                "metadata": {"type": "object", "additionalProperties": True},
            },
            "required": ["result_type"],
            "additionalProperties": True,
        }

    # ========== Connection Management ==========

    def connect(self) -> None:
        """Connect to the WHO knowledge source.
        
        Establishes repository and provider instances. In this implementation,
        the connection is verified by attempting a simple query.
        
        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            if self._session is None:
                raise ConnectionError("No database session provided to WHO plugin")
            
            # Initialize repository with session
            self._repository = WHOKnowledgeRepository(self._session)
            
            # Initialize provider with repository
            self._provider = WHOProvider(self._repository)
            
            # Verify connection by checking metadata
            metadata = self._provider.metadata()
            if metadata is None:
                raise ConnectionError("Failed to retrieve WHO provider metadata")
            
            self._is_connected = True
            logger.info(f"{self.plugin_name} connected to database")
        
        except Exception as exc:
            logger.error(f"Failed to connect {self.plugin_name}: {exc}")
            raise ConnectionError(f"WHO Knowledge Plugin connection failed: {exc}") from exc

    def disconnect(self) -> None:
        """Disconnect from the WHO knowledge source.
        
        Cleans up repository and provider instances. The database session
        is managed externally and not closed here.
        """
        try:
            self._repository = None
            self._provider = None
            self._is_connected = False
            logger.info(f"{self.plugin_name} disconnected")
        except Exception as exc:
            logger.error(f"Error disconnecting {self.plugin_name}: {exc}")
            # Don't raise on disconnect; graceful cleanup

    # ========== Query Methods ==========

    def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search WHO knowledge base with text query.
        
        Supports searching for diseases, drugs, and other clinical entities.
        
        Args:
            query: Search text (e.g., disease name, antibiotic name, symptom)
            filters: Optional filtering criteria (not yet used)
        
        Returns:
            List of structured WHO knowledge results
        
        Raises:
            ConnectionError: If knowledge source is unavailable
        """
        if not query or not query.strip():
            return []

        if not self.validate():
            raise ConnectionError(f"{self.plugin_name} is not ready")
        
        try:
            query_text = query.strip()
            results = []
            
            # Search for diseases
            diseases = self._repository.search_diseases(query_text)
            for disease in diseases:
                result = WHOKnowledgeResult(
                    plugin_version=self.plugin_version,
                    knowledge_version=self.knowledge_version(),
                    result_type="disease",
                    entity_id=disease.disease_id,
                    entity_name=disease.name,
                    entity_description=disease.description or "",
                    clinical_recommendation=f"See disease guidelines for {disease.name}",
                    evidence_level="HIGH",
                    citation=f"WHO Guidelines - {disease.name}",
                    source_version="WHO 2023",
                    metadata={
                        "care_level": getattr(disease, "care_level", None),
                        "chapter": getattr(disease, "chapter_number", None),
                        "disease_id": disease.disease_id,
                    },
                )
                results.append(result.to_dict())
            
            # Search for drugs
            all_drugs = self._repository.list_drugs()
            drugs = [d for d in all_drugs if query_text.lower() in (d.generic_name or "").lower()]
            
            for drug in drugs:
                result = WHOKnowledgeResult(
                    plugin_version=self.plugin_version,
                    knowledge_version=self.knowledge_version(),
                    result_type="drug",
                    entity_id=drug.drug_id,
                    entity_name=drug.generic_name or "",
                    entity_description=getattr(drug, "notes", ""),
                    guideline_category=getattr(drug, "aware_group", ""),
                    clinical_recommendation=f"{drug.generic_name} is WHO {getattr(drug, 'aware_group', 'unclassified')}",
                    evidence_level="HIGH",
                    citation="WHO AWaRe Classification",
                    source_version="WHO 2023",
                    metadata={
                        "aware_group": getattr(drug, "aware_group", None),
                        "antibiotic_class": getattr(drug, "antibiotic_class", None),
                        "route": getattr(drug, "route", None),
                        "drug_id": drug.drug_id,
                    },
                )
                results.append(result.to_dict())
            
            logger.info(f"{self.plugin_name} search for '{query_text}' returned {len(results)} results")
            return results
        
        except Exception as exc:
            logger.error(f"Search failed in {self.plugin_name}: {exc}")
            raise ConnectionError(f"WHO search failed: {exc}") from exc

    def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Query WHO knowledge with structured criteria.
        
        Supports structured queries for specific clinical scenarios.
        
        Args:
            criteria: Query criteria (e.g., {"disease_id": "...", "severity": "..."})
        
        Returns:
            Structured WHO knowledge result, or empty dict if no match
        
        Raises:
            ConnectionError: If knowledge source is unavailable
            ValueError: If criteria is invalid
        """
        
        if not criteria or not isinstance(criteria, dict):
            return {}

        if not self.validate():
            raise ConnectionError(f"{self.plugin_name} is not ready")
        
        try:
            # Query by disease ID
            if "disease_id" in criteria:
                disease_id = criteria["disease_id"]
                disease = self._repository.get_disease_by_id(disease_id)
                
                if disease is None:
                    return {}
                
                # Get complete guideline with all related entities
                guideline = self._repository.get_complete_guideline(disease_id)
                
                # Build comprehensive result
                recommendations = []
                if guideline and hasattr(guideline, "recommendations"):
                    for rec in guideline.recommendations:
                        recommendations.append({
                            "drug": getattr(rec, "drug_id", ""),
                            "population": getattr(rec, "population", ""),
                            "severity": getattr(rec, "severity", ""),
                        })
                
                result = WHOKnowledgeResult(
                    plugin_version=self.plugin_version,
                    knowledge_version=self.knowledge_version(),
                    result_type="disease_guideline",
                    entity_id=disease.disease_id,
                    entity_name=disease.name,
                    entity_description=disease.description or "",
                    clinical_recommendation=f"Follow WHO guidelines for {disease.name}",
                    evidence_level="HIGH",
                    citation=f"WHO Guidelines - {disease.name}",
                    source_version="WHO 2023",
                    metadata={
                        "disease_id": disease.disease_id,
                        "recommendations_count": len(recommendations),
                        "care_level": getattr(disease, "care_level", None),
                    },
                )
                return result.to_dict()
            # Query by drug
            if "drug_name" in criteria:
                drug_name = criteria["drug_name"]
                drug = self._repository.get_drug_by_name(drug_name)
                
                if drug is None:
                    return {}
                
                result = WHOKnowledgeResult(
                    plugin_version=self.plugin_version,
                    knowledge_version=self.knowledge_version(),
                    result_type="drug_guideline",
                    entity_id=drug.drug_id,
                    entity_name=drug.generic_name or "",
                    entity_description=getattr(drug, "notes", ""),
                    guideline_category=getattr(drug, "aware_group", ""),
                    clinical_recommendation=f"{drug.generic_name} is WHO {getattr(drug, 'aware_group', 'unclassified')}",
                    evidence_level="HIGH",
                    citation="WHO AWaRe Classification",
                    source_version="WHO 2023",
                    metadata={
                        "drug_id": drug.drug_id,
                        "aware_group": getattr(drug, "aware_group", None),
                        "antibiotic_class": getattr(drug, "antibiotic_class", None),
                    },
                )
                return result.to_dict()
            
            # No matching query criteria
            return {}
        
        except Exception as exc:
            logger.error(f"Query failed in {self.plugin_name}: {exc}")
            raise ValueError(f"WHO query failed: {exc}") from exc

    # ========== Domain and Version Methods ==========

    def supported_domains(self) -> List[str]:
        """Return supported clinical domains.
        
        WHO guidelines apply broadly to all respiratory infection contexts.
        """
        return [
            "respiratory",
            "gastrointestinal",
            "urinary_tract",
            "wound",
            "bloodstream",
            "meningitis",
            "general",  # Applies across domains
        ]

    def knowledge_version(self) -> str:
        """Return WHO knowledge data version."""
        return "WHO 2023"

    # ========== Plugin-Specific Methods (for explainability) ==========

    def explain(self, entity_id: str, entity_type: str = "disease") -> Dict[str, Any]:
        """Generate explainable evidence for an entity.
        
        Returns structured clinical reasoning that can be presented to clinicians.
        
        Args:
            entity_id: ID of the entity to explain
            entity_type: Type of entity ("disease", "drug", "recommendation")
        
        Returns:
            Dictionary with explainable information
        """
        if not self.validate():
            raise ConnectionError(f"{self.plugin_name} is not ready")
        
        try:
            explanation = {
                "source": "WHO",
                "plugin_version": self.plugin_version,
                "knowledge_version": self.knowledge_version(),
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evidence": [],
                "recommendations": [],
            }
            
            if entity_type == "disease":
                disease = self._repository.get_complete_guideline(entity_id)
                if disease:
                    explanation["entity_name"] = disease.name
                    explanation["description"] = disease.description
                    
                    # Collect evidence
                    if hasattr(disease, "evidence"):
                        for evidence in disease.evidence:
                            explanation["evidence"].append({
                                "evidence_id": evidence.evidence_id,
                                "text": getattr(evidence, "text", ""),
                                "type": getattr(evidence, "type", ""),
                                "source": getattr(evidence, "source", "WHO"),
                            })
                    
                    # Collect recommendations
                    if hasattr(disease, "recommendations"):
                        for rec in disease.recommendations:
                            explanation["recommendations"].append({
                                "recommendation_id": rec.recommendation_id,
                                "drug": getattr(rec, "drug_id", ""),
                                "population": getattr(rec, "population", ""),
                                "severity": getattr(rec, "severity", ""),
                            })
            
            elif entity_type == "drug":
                drug = self._repository.get_drug_by_id(entity_id)
                if drug:
                    explanation["entity_name"] = drug.generic_name
                    explanation["aware_category"] = getattr(drug, "aware_group", "")
                    explanation["antibiotic_class"] = getattr(drug, "antibiotic_class", "")
                    explanation["route"] = getattr(drug, "route", "")
                    explanation["clinical_notes"] = getattr(drug, "notes", "")
            
            return explanation
        
        except Exception as exc:
            logger.error(f"Explain failed in {self.plugin_name}: {exc}")
            raise
