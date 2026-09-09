# Phase 25G: Backend Dependency Reproducibility

`jsonschema` was imported by `tests/test_soar_deployment_contract.py` and `tests/test_plugin_input_schema_contract.py` but was absent from `apps/api/requirements.txt`. It was added as `jsonschema>=4.23.0`.

`pytest` and `flake8` remain CI tools installed explicitly by the workflow. Runtime and test dependencies are now separated appropriately: `jsonschema` is declared in backend requirements because the backend test suite imports it.

The focused SOAR tests ran successfully after installing the declared dependency: **12 passed**.
