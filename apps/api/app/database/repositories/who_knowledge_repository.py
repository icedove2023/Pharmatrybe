from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database.repositories.base_repository import BaseRepository
from app.database.repositories.clinical_case_repository import RepositoryError
from app.models.disease import Disease
from app.models.recommendation import Recommendation
from app.models.evidence import Evidence
from app.models.diagnostic import Diagnostic
from app.models.monitoring import Monitoring
from app.models.referral import Referral
from app.models.follow_up import FollowUp
from app.models.stewardship import Stewardship
from app.models.drug import Drug
from app.models.pathogen import Pathogen

class WHOKnowledgeRepository(BaseRepository[object]):
    """Repository for retrieving WHO knowledge base entities."""

    def create(self, entity: object) -> object:
        raise RepositoryError("Create is not supported by WHOKnowledgeRepository")

    def get_by_id(self, entity_id: int) -> object | None:
        raise RepositoryError("Use the WHO-specific retrieval methods instead")

    def get_all(self) -> list[object]:
        raise RepositoryError("Use list_diseases or list_drugs instead")

    def update(self, entity_id: int, **kwargs: Any) -> object | None:
        raise RepositoryError("Update is not supported by WHOKnowledgeRepository")

    def delete(self, entity_id: int) -> None:
        raise RepositoryError("Delete is not supported by WHOKnowledgeRepository")

    def _scalar(self, statement):
        try:
            return self.session.scalar(statement)
        except SQLAlchemyError as exc:
            raise RepositoryError(f"Unable to execute scalar query: {exc}") from exc

    def _scalars(self, statement):
        try:
            return list(self.session.scalars(statement).all())
        except SQLAlchemyError as exc:
            raise RepositoryError(f"Unable to execute list query: {exc}") from exc

    def get_disease_by_id(self, disease_id: str) -> Disease | None:
        statement = select(Disease).where(Disease.disease_id == disease_id)
        return self._scalar(statement)

    def get_disease_by_name(self, name: str) -> Disease | None:
        statement = select(Disease).where(Disease.name == name)
        return self._scalar(statement)

    def search_diseases(self, query: str) -> list[Disease]:
        query_text = f"%{query}%"
        statement = select(Disease).where(
            or_(
                Disease.name.ilike(query_text),
                Disease.description.ilike(query_text),
            )
        )
        return self._scalars(statement)

    def list_diseases(self) -> list[Disease]:
        statement = select(Disease)
        return self._scalars(statement)

    def get_drug_by_id(self, drug_id: str) -> Drug | None:
        statement = select(Drug).where(Drug.drug_id == drug_id)
        return self._scalar(statement)

    def get_drug_by_name(self, name: str) -> Drug | None:
        statement = select(Drug).where(Drug.generic_name == name)
        return self._scalar(statement)

    def list_drugs(self) -> list[Drug]:
        statement = select(Drug)
        return self._scalars(statement)

    def get_recommendation_by_id(self, recommendation_id: str) -> Recommendation | None:
        statement = select(Recommendation).where(Recommendation.recommendation_id == recommendation_id)
        return self._scalar(statement)

    def get_recommendations_by_disease(self, disease_id: str) -> list[Recommendation]:
        statement = select(Recommendation).where(Recommendation.disease_id == disease_id)
        return self._scalars(statement)

    def get_recommendations_by_population(self, population: str) -> list[Recommendation]:
        statement = select(Recommendation).where(Recommendation.population == population)
        return self._scalars(statement)

    def get_recommendations_by_severity(self, severity: str) -> list[Recommendation]:
        statement = select(Recommendation).where(Recommendation.severity == severity)
        return self._scalars(statement)

    def get_recommendations_by_drug(self, drug_id: str) -> list[Recommendation]:
        statement = select(Recommendation).where(Recommendation.drug_id == drug_id)
        return self._scalars(statement)

    def get_evidence_for_disease(self, disease_id: str) -> list[Evidence]:
        statement = select(Evidence).where(Evidence.disease_id == disease_id)
        return self._scalars(statement)

    def get_diagnostics(self, disease_id: str) -> list[Diagnostic]:
        statement = select(Diagnostic).where(Diagnostic.disease_id == disease_id)
        return self._scalars(statement)

    def get_monitoring(self, disease_id: str) -> list[Monitoring]:
        statement = select(Monitoring).where(Monitoring.disease_id == disease_id)
        return self._scalars(statement)

    def get_follow_up(self, disease_id: str) -> list[FollowUp]:
        statement = select(FollowUp).where(FollowUp.disease_id == disease_id)
        return self._scalars(statement)

    def get_referral(self, disease_id: str) -> list[Referral]:
        statement = select(Referral).where(Referral.disease_id == disease_id)
        return self._scalars(statement)

    def get_stewardship(self, disease_id: str) -> list[Stewardship]:
        statement = select(Stewardship).where(Stewardship.disease_id == disease_id)
        return self._scalars(statement)

    def get_pathogens_for_disease(self, disease_id: str) -> list[Pathogen]:
        statement = select(Disease).options(selectinload(Disease.pathogens)).where(Disease.disease_id == disease_id)
        disease = self._scalar(statement)
        return disease.pathogens if disease is not None else []

    def get_pathogens_for_recommendation(self, recommendation_id: str) -> list[Pathogen]:
        statement = select(Recommendation).options(selectinload(Recommendation.pathogens)).where(
            Recommendation.recommendation_id == recommendation_id
        )
        recommendation = self._scalar(statement)
        return recommendation.pathogens if recommendation is not None else []

    def get_complete_guideline(self, disease_id: str) -> Disease | None:
        statement = (
            select(Disease)
            .options(
                selectinload(Disease.pathogens),
                selectinload(Disease.evidence),
                selectinload(Disease.diagnostics),
                selectinload(Disease.stewardship),
                selectinload(Disease.monitoring),
                selectinload(Disease.follow_up),
                selectinload(Disease.referral),
                selectinload(Disease.recommendations)
                .selectinload(Recommendation.drug),
                selectinload(Disease.recommendations)
                .selectinload(Recommendation.evidence),
                selectinload(Disease.recommendations)
                .selectinload(Recommendation.pathogens),
            )
            .where(Disease.disease_id == disease_id)
        )
        return self._scalar(statement)
