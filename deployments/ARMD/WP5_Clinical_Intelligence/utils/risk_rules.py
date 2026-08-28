"""
WP5 Module 3

Clinical Risk Rules

Deterministic rules used to generate the
Clinical Risk Profile.

IMPORTANT

These are NOT machine learning rules.

These are transparent, deterministic clinical
heuristics derived from recognised antimicrobial
stewardship principles.

The Decision Engine may later replace or extend
these rules.
"""

from __future__ import annotations

from typing import Any


# ============================================================
# Overall Resistance Risk
# ============================================================

def determine_overall_risk(score: int) -> str:
    """
    Convert accumulated score into
    an overall AMR risk category.
    """

    if score >= 10:
        return "Very High"

    if score >= 7:
        return "High"

    if score >= 4:
        return "Moderate"

    return "Low"


# ============================================================
# Healthcare Exposure
# ============================================================

def determine_healthcare_exposure(
    previous_admissions: int,
    hospital_days: int,
) -> str:
    """
    Determine healthcare exposure.
    """

    if hospital_days >= 30 or previous_admissions >= 3:
        return "Extensive"

    if hospital_days >= 7 or previous_admissions >= 1:
        return "Moderate"

    return "Minimal"


# ============================================================
# Previous Antibiotic Exposure
# ============================================================

def determine_antibiotic_exposure(
    antibiotic_courses: int,
) -> str:
    """
    Estimate previous antibiotic exposure.
    """

    if antibiotic_courses >= 3:
        return "High"

    if antibiotic_courses >= 1:
        return "Present"

    return "None"


# ============================================================
# ICU Exposure
# ============================================================

def determine_icu_status(
    icu: bool,
) -> str:
    """
    ICU exposure.
    """

    return "Yes" if icu else "No"


# ============================================================
# Recent Hospitalisation
# ============================================================

def determine_recent_hospitalisation(
    admitted_last_90_days: bool,
) -> str:
    """
    Recent admission status.
    """

    return "Yes" if admitted_last_90_days else "No"


# ============================================================
# Hospital Acquisition
# ============================================================

def determine_acquisition(
    healthcare_exposure: str,
    icu: bool,
) -> str:
    """
    Estimate infection acquisition category.
    """

    if icu:
        return "Hospital Acquired"

    if healthcare_exposure in (
        "Moderate",
        "Extensive",
    ):
        return "Healthcare Associated"

    return "Community"


# ============================================================
# MDR Risk
# ============================================================

def determine_mdr_risk(
    overall_risk: str,
    previous_antibiotics: str,
    icu: bool,
) -> str:
    """
    Estimate multidrug resistance risk.
    """

    if overall_risk == "Very High":
        return "High"

    if icu:
        return "High"

    if previous_antibiotics == "High":
        return "High"

    if overall_risk == "High":
        return "Moderate"

    return "Low"


# ============================================================
# Stewardship Priority
# ============================================================

def determine_stewardship_priority(
    overall_risk: str,
) -> tuple[str, str]:
    """
    Stewardship review level.

    Returns
    -------
    priority
    message
    """

    if overall_risk == "Very High":

        return (
            "Urgent",
            (
                "High antimicrobial resistance risk. "
                "Review empirical therapy using "
                "local susceptibility data."
            ),
        )

    if overall_risk == "High":

        return (
            "Review",
            (
                "Antimicrobial stewardship review "
                "recommended."
            ),
        )

    return (
        "Routine",
        (
            "Routine antimicrobial stewardship "
            "practice recommended."
        ),
    )


# ============================================================
# Clinical Risk Score
# ============================================================

def calculate_risk_score(patient: dict[str, Any]) -> int:
    """
    Compute a simple deterministic risk score.

    This score is NOT machine learning.

    It is used only to classify the
    patient's resistance risk.
    """

    score = 0

    if patient.get("ICU", False):
        score += 3

    if patient.get("Previous_Antibiotic_Courses", 0) >= 3:
        score += 3

    elif patient.get("Previous_Antibiotic_Courses", 0) >= 1:
        score += 2

    if patient.get("Hospital_Days", 0) >= 14:
        score += 2

    if patient.get("Previous_Admissions", 0) >= 2:
        score += 2

    if patient.get("Admitted_Last_90_Days", False):
        score += 2

    return score