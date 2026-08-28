from pathlib import Path


def test_expected_files_exist():
    base = Path(__file__).parent.parent
    expected = [
        "plugin.yaml",
        "armd_prediction_plugin.py",
        "runtime_context.py",
        "preprocessing.py",
        "artifact_loader.py",
        "model_registry.py",
        "prediction_engine.py",
        "ranking.py",
        "explainability.py",
        "audit.py",
        "contracts",
        "tests",
    ]
    for p in expected:
        assert (base / p).exists(), f"Missing {p} in ARMD plugin skeleton"
