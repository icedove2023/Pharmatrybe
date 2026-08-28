"""
WP5 Module 3

Clinical Risk Profile Service

Generates a structured Clinical Risk Profile
using deterministic clinical rules.

This service contains NO machine learning.

It transforms patient features into a structured
clinical assessment suitable for downstream
Decision Engine consumption.
"""

from __future__ import annotations

from typing import Any

from ..schemas import (
    ClinicalRiskFactor,
    ClinicalRiskProfile,
    StewardshipAlert,
)

from ..utils.risk_rules import (
    calculate_risk_score,
    determine_acquisition,
    determine_antibiotic_exposure,
    determine_healthcare_exposure,
    determine_icu_status,
    determine_mdr_risk,
    determine_overall_risk,
    determine_recent_hospitalisation,
    determine_stewardship_priority,
)


class RiskProfileService:
    """
    Generate a structured clinical risk profile.
    """

    def generate(
        self,
        patient: dict[str, Any],
        
    ) -> ClinicalRiskProfile:
        """
        Generate Clinical Risk Profile.
        """

        # --------------------------------------------------
        # Raw patient values
        # --------------------------------------------------

        previous_admissions = patient.get(
            "Previous_Admissions",
            0,
        )

        hospital_days = patient.get(
            "Hospital_Days",
            0,
        )

        previous_antibiotics = patient.get(
            "Previous_Antibiotic_Courses",
            0,
        )

        icu = patient.get(
            "ICU",
            False,
        )

        recent_admission = patient.get(
            "Admitted_Last_90_Days",
            False,
        )

        # --------------------------------------------------
        # Clinical rules
        # --------------------------------------------------

        score = calculate_risk_score(patient)

        overall_risk = determine_overall_risk(score)

        healthcare_exposure = determine_healthcare_exposure(
            previous_admissions,
            hospital_days,
        )

        antibiotic_exposure = determine_antibiotic_exposure(
            previous_antibiotics,
        )

        icu_status = determine_icu_status(
            icu,
        )

        recent_status = determine_recent_hospitalisation(
            recent_admission,
        )

        acquisition = determine_acquisition(
            healthcare_exposure,
            icu,
        )

        mdr_risk = determine_mdr_risk(
            overall_risk,
            antibiotic_exposure,
            icu,
        )

        priority, message = determine_stewardship_priority(
            overall_risk,
        )

        # --------------------------------------------------
        # Contributing factors
        # --------------------------------------------------

        factors = [

            ClinicalRiskFactor(
                factor="Previous Admissions",
                status=str(previous_admissions),
                risk_level=healthcare_exposure,
                explanation=(
                    "Frequent hospital admissions increase "
                    "healthcare-associated resistance risk."
                ),
            ),

            ClinicalRiskFactor(
                factor="Hospital Stay",
                status=f"{hospital_days} days",
                risk_level=healthcare_exposure,
                explanation=(
                    "Longer hospital stay increases exposure "
                    "to resistant organisms."
                ),
            ),

            ClinicalRiskFactor(
                factor="Previous Antibiotic Courses",
                status=str(previous_antibiotics),
                risk_level=antibiotic_exposure,
                explanation=(
                    "Repeated antibiotic exposure selects "
                    "for resistant organisms."
                ),
            ),

            ClinicalRiskFactor(
                factor="ICU Admission",
                status=icu_status,
                risk_level="High" if icu else "Low",
                explanation=(
                    "ICU patients have increased risk of "
                    "multidrug-resistant pathogens."
                ),
            ),

            ClinicalRiskFactor(
                factor="Recent Hospitalisation",
                status=recent_status,
                risk_level="Moderate" if recent_admission else "Low",
                explanation=(
                    "Recent admission may indicate healthcare "
                    "associated exposure."
                ),
            ),
        ]

        # --------------------------------------------------
        # Return profile
        # --------------------------------------------------

        return ClinicalRiskProfile(

            overall_risk=overall_risk,

            healthcare_exposure=healthcare_exposure,

            previous_antibiotic_exposure=antibiotic_exposure,

            icu_exposure=icu_status,

            hospital_acquisition=acquisition,

            recent_hospitalisation=recent_status,

            mdr_risk=mdr_risk,

            stewardship=StewardshipAlert(
                priority=priority,
                message=message,
            ),

            contributing_factors=factors,
        )