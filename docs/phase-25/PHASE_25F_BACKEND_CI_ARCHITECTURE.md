# Phase 25F: Backend CI Architecture

## Previous workflow
`.github/workflows/python-package-conda.yml` already used the `apps/api` working directory and installed backend requirements, pytest, and Flake8. Its critical lint gate scanned `.` and selected `E9,F63,F7,F82`, omitting `F821`; it had no separate quality report.

## Final workflow
The existing workflow was preserved and minimally updated:
- Python `3.11`, matching the backend project requirement.
- Critical lint scope: `flake8 app tests`.
- Critical selectors: `E9,F63,F7,F82,F821`.
- Added a non-blocking `flake8 app tests --exit-zero` quality report with complexity and line-length settings.
- Existing backend test step remains `python -m pytest tests -ra`.

The final critical command completed with exit code 0 and reported no errors. No blanket F821 suppression was added.
