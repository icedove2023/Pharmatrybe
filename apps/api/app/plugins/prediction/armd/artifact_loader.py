from __future__ import annotations


class ARMDArtifactLoader:
    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def load(self, artifact_path: str) -> object:
        raise NotImplementedError("ARMD artifact loading is not implemented")
