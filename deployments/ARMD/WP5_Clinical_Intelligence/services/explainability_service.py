"""
WP5 Module 2

Explainability Service

Converts the raw SHAP output produced by the
WP4 Decision Engine into a structured,
API-friendly explainability object.
"""

from __future__ import annotations

from typing import Dict, List

from ..schemas.structuredexplainability import (
    ClinicalDriver,
    ExplainabilityPlots,
    StructuredExplainability,
)


class ExplainabilityService:
    """
    Converts WP4 SHAP output into structured explainability.
    """

    def generate(
        self,
        patient_features,
        prediction_df,
        patient=None,
        shap_result=None,
    ) -> StructuredExplainability | None:
        """
        Build explainability for the highest-risk antibiotic.
        """

        if prediction_df.empty:
            return None

        # Highest predicted probability
        row = (
            prediction_df
            .sort_values("probability", ascending=False)
            .iloc[0]
        )

        prediction_antibiotic = str(row["antibiotic"])
        probability = float(row["probability"])

        # Use the SHAP result produced by WP4 if available,
        # otherwise fall back to an empty explanation.
        shap_output = shap_result or {
            "positive_drivers": [],
            "negative_drivers": [],
            "figure_paths": {},
            "base_value": probability,
        }

        antibiotic = shap_output.get("antibiotic") or prediction_antibiotic

        return self.build(
            antibiotic=antibiotic,
            prediction_probability=probability,
            shap_output=shap_output,
        )

    # ---------------------------------------------------------

    def build(
        self,
        antibiotic: str,
        prediction_probability: float,
        shap_output: Dict,
    ) -> StructuredExplainability:

        positive = self._convert_positive(
            shap_output.get("positive_drivers", [])
        )

        negative = self._convert_negative(
            shap_output.get("negative_drivers", [])
        )

        plots = ExplainabilityPlots(
            waterfall=shap_output.get("figure_paths", {}).get("waterfall"),
            bar=shap_output.get("figure_paths", {}).get("bar"),
            beeswarm=shap_output.get("figure_paths", {}).get("beeswarm"),
            force=shap_output.get("figure_paths", {}).get("force"),
        )

        return StructuredExplainability(
            antibiotic=antibiotic,
            model=antibiotic,
            expected_probability=shap_output.get("base_value"),
            predicted_probability=prediction_probability,
            narrative=shap_output.get("narrative"),
            top_positive_drivers=positive,
            top_negative_drivers=negative,
            plots=plots,
        )

    # ---------------------------------------------------------

    def _convert_positive(
        self,
        drivers: List,
    ) -> List[ClinicalDriver]:

        output = []

        for feature, value in drivers:

            output.append(
                ClinicalDriver(
                    feature=feature,
                    feature_value=None,
                    shap_value=float(value),
                    impact="Increase Resistance",
                    magnitude=abs(float(value)),
                )
            )

        return output

    # ---------------------------------------------------------

    def _convert_negative(
        self,
        drivers: List,
    ) -> List[ClinicalDriver]:

        output = []

        for feature, value in drivers:

            output.append(
                ClinicalDriver(
                    feature=feature,
                    feature_value=None,
                    shap_value=float(value),
                    impact="Decrease Resistance",
                    magnitude=abs(float(value)),
                )
            )

        return output