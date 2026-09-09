# Phase 25A: CI Failure Reproduction

## Workflow
- File: `.github/workflows/python-package-conda.yml`
- Job: `Backend Tests` (job id `backend-test`)
- Runner: `ubuntu-latest`
- Working directory: `apps/api`
- Python before this phase: `3.10`
- Python after this phase: `3.11`, matching `apps/api/pyproject.toml` (`>=3.11`)

## Commands
The workflow installed `requirements.txt`, then `pytest` and `flake8`. Its original critical command was:

```text
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

It did not select `F821`. Local reproduction with the requested selector used:

```text
python -m flake8 . --count --select=E9,F63,F7,F82,F821 --show-source --statistics
```

Flake8 reproduction version: `7.3.0`; local Python: `3.12.10`.

## Finding
The original workflow scanned all files under `apps/api` but omitted `F821` from the critical selector. The equivalent command including `F821` measured 23 undefined-name errors. No `.flake8`, `setup.cfg`, or `tox.ini` configuration was found. The workflow was therefore not enforcing the failure class described by this phase.
