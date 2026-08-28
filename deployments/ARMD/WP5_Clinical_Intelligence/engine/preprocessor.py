"""
WP5 Preprocessor

Thin wrapper around the validated WP4 preprocessing
pipeline.

This module MUST NOT duplicate preprocessing logic.

All feature engineering remains inside WP4.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from WP4_Decision_Engine import (
    load_wp2_table,
    load_wp3_artifacts,
    load_patient,
    preprocess_patient_features,
)


class Preprocessor:
    """
    Wrapper around WP4 preprocessing.
    """

    def __init__(self) -> None:

        self._artifacts = load_wp3_artifacts()

        self._wp2 = load_wp2_table()

    @property
    def artifacts(self):

        return self._artifacts

    def load_patient(self, patient_id: int) -> pd.Series:
        """
        Load a patient from the WP2 table.
        """

        return load_patient(
            self._wp2,
            patient_id,
        )

    def preprocess(
        self,
        patient: pd.Series | dict[str, Any],
    ) -> pd.DataFrame:
        """
        Convert a raw patient record into
        the WP4 model feature space.
        """

        if isinstance(patient, dict):

            patient = pd.Series(patient)

        features = preprocess_patient_features(
            patient,
            self._artifacts,
        )

        return features