"""
WP5 Module 2

Explainability Formatter

Converts the raw WP4 SHAP output into the
official WP5 structured explainability schema.

This module contains NO machine learning.

It simply translates technical SHAP outputs into
clinical intelligence objects.
"""

from __future__ import annotations

from typing import Dict
from typing import List

from ..schemas.structuredexplainability import ClinicalDriver
from ..schemas.structuredexplainability import ExplainabilityPlots
from ..schemas.structuredexplainability import StructuredExplainability


class ExplainabilityFormatter:
    """
    Converts WP4 SHAP output into WP5 schema.
    """

    @staticmethod
    def _driver_list(
        drivers: List[tuple],
        patient_values: Dict,
        increase: bool,
    ) -> List[ClinicalDriver]:
        """
        Convert SHAP tuples into ClinicalDriver objects.
        """

        clinical_drivers = []

        for feature, shap_value in drivers:

            clinical_drivers.append(

                ClinicalDriver(

                    feature=feature,

                    feature_value=str(
                        patient_values.get(feature, "")
                    ),

                    shap_value=float(shap_value),

                    impact=(
                        "Increase Resistance"
                        if increase
                        else "Decrease Resistance"
                    ),

                    magnitude=abs(float(shap_value)),
                )

            )

        return clinical_drivers

    @classmethod
    def build(
        cls,
        shap_output: Dict,
        patient_values: Dict,
        antibiotic: str,
    ) -> StructuredExplainability:
        """
        Convert raw SHAP dictionary from WP4 into
        StructuredExplainability.
        """

        plots = ExplainabilityPlots(
            waterfall=shap_output.get("figure_paths", {}).get("waterfall"),
            bar=shap_output.get("figure_paths", {}).get("bar"),
            beeswarm=shap_output.get("figure_paths", {}).get("beeswarm"),
            force=shap_output.get("figure_paths", {}).get("force"),
        )

        positive = cls._driver_list(
            shap_output.get("positive_drivers", []),
            patient_values,
            increase=True,
        )

        negative = cls._driver_list(
            shap_output.get("negative_drivers", []),
            patient_values,
            increase=False,
        )

        return StructuredExplainability(

            model=antibiotic,

            expected_probability=shap_output.get(
                "base_value"
            ),

            predicted_probability=shap_output.get(
                "probability"
            ),

            top_positive_drivers=positive,

            top_negative_drivers=negative,

            narrative=shap_output.get(
                "narrative"
            ),

            plots=plots,
        )