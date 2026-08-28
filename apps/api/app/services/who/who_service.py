from __future__ import annotations

from typing import Any

from app.knowledge.models.knowledge_bundle import KnowledgePackage
from app.knowledge.orchestrator.knowledge_orchestrator import KnowledgeOrchestrator
from app.knowledge.providers.query_models import KnowledgeQuery, SearchQuery


class WHOServiceError(RuntimeError):
    """Raised when the WHO service cannot complete an operation."""


class WHOService:
    """Service orchestrator for WHO knowledge retrieval."""

    def __init__(self, orchestrator: KnowledgeOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator

    def _get_orchestrator(self) -> KnowledgeOrchestrator:
        if self.orchestrator is None:
            raise WHOServiceError("No knowledge orchestrator configured for the WHO service")
        return self.orchestrator

    def _wrap_orchestrator_error(self, exc: Exception) -> WHOServiceError:
        return WHOServiceError(str(exc))

    def _first_successful_package(self, results: list[Any]) -> KnowledgePackage | None:
        for result in results:
            if getattr(result, "status", None) == "success" and getattr(result, "knowledge_package", None) is not None:
                package = result.knowledge_package
                if isinstance(package, KnowledgePackage):
                    return package
        return None

    def _get_package(self, query: KnowledgeQuery) -> KnowledgePackage | None:
        results = self._get_orchestrator().retrieve(query)
        return self._first_successful_package(results)

    def _search_packages(self, query: SearchQuery) -> list[KnowledgePackage]:
        results = self._get_orchestrator().search(query)
        packages: list[KnowledgePackage] = []
        for result in results:
            if getattr(result, "status", None) == "success" and getattr(result, "knowledge_package", None) is not None:
                package = result.knowledge_package
                if isinstance(package, list):
                    packages.extend(package)
                elif isinstance(package, KnowledgePackage):
                    packages.append(package)
        return packages

    def get_disease_by_id(self, disease_id: str) -> Any | None:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.diseases[0] if package and package.diseases else None
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_disease_by_name(self, name: str) -> Any | None:
        try:
            packages = self._search_packages(SearchQuery(query_text=name, entity_type="disease"))
            for package in packages:
                for disease in package.diseases or []:
                    if getattr(disease, "title", None) == name or getattr(disease, "name", None) == name:
                        return disease
            return None
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def search_diseases(self, query: str) -> list[Any]:
        try:
            packages = self._search_packages(SearchQuery(query_text=query, entity_type="disease"))
            diseases: list[Any] = []
            for package in packages:
                diseases.extend(package.diseases or [])
            return diseases
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def list_supported_diseases(self) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease"))
            return package.diseases or []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_guideline_by_disease_id(self, disease_id: str) -> KnowledgePackage | None:
        try:
            return self._get_package(KnowledgeQuery(entity_type="guideline", identifier=disease_id))
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_guideline_by_disease_name(self, name: str) -> KnowledgePackage | None:
        try:
            disease = self.get_disease_by_name(name)
            if disease is None:
                return None
            disease_id = getattr(disease, "disease_id", None) or getattr(disease, "id", None)
            if disease_id is None:
                return None
            return self.get_guideline_by_disease_id(disease_id)
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_recommendations(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.recommendations or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_evidence(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.evidence or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_diagnostics(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.diagnostics or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_monitoring(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.monitoring or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_follow_up(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.follow_up or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_referral(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.referral or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_stewardship(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.stewardship or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc

    def get_pathogens(self, disease_id: str) -> list[Any]:
        try:
            package = self._get_package(KnowledgeQuery(entity_type="disease", identifier=disease_id))
            return package.pathogens or [] if package is not None else []
        except Exception as exc:
            raise self._wrap_orchestrator_error(exc) from exc
