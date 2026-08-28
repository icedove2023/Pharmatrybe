"""Central API router aggregation for the PharmaTrybe backend."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.armd import router as armd_router
from app.api.v1.auth import router as auth_router
from app.api.v1.clinical_cases import router as clinical_cases_router
from app.api.v1.decision import router as decision_router
from app.api.v1.explainability import router as explainability_router
from app.api.v1.health import router as health_router
from app.api.v1.patients import router as patients_router
from app.api.v1.pipeline import router as pipeline_router
from app.api.v1.plugins import router as plugins_router
from app.api.v1.professionals import router as professionals_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.soar import router as soar_router
from app.api.v1.version import router as version_router
from app.api.v1.who import router as who_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(clinical_cases_router)
router.include_router(patients_router)
router.include_router(pipeline_router)
router.include_router(professionals_router)
router.include_router(recommendations_router)
router.include_router(who_router)
router.include_router(soar_router)
router.include_router(armd_router)
router.include_router(decision_router)
router.include_router(explainability_router)
router.include_router(plugins_router)
router.include_router(admin_router)
router.include_router(health_router)
router.include_router(version_router)
