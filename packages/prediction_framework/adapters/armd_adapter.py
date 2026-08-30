"""Importable compatibility wrapper for the shared ARMD adapter."""

from pathlib import Path

_source = Path(__file__).resolve().parents[2] / "prediction-framework" / "adapters" / "armd_adapter.py"
exec(compile(_source.read_text(encoding="utf-8"), str(_source), "exec"), globals())
