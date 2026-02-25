# Conductor Journal

## 2026-02-25 - Release v2.1.3 Security Patch & Sync

**Observation:** Version 2.1.3 (Security Fix) was found in `opencore/__init__.py` but missing from `CHANGELOG.md`. Versions 2.1.1 and 2.1.2 were entirely missing from history.
**Action:** Updated `CHANGELOG.md` to document v2.1.3 and marked v2.1.1/v2.1.2 as skipped/internal. Rebuilt frontend artifacts to ensure consistency. Verified backend stability.

## 2026-02-24 - Emergency Fix for Dependency Regression (v2.0.6)

**Observation:** User reported `ModuleNotFoundError: No module named 'google_auth_oauthlib'` on `opencore start`. This dependency was missing in `pyproject.toml` despite being in `requirements.txt`. Additionally, `google-generativeai` was listed but deprecated.
**Action:** Removed `google-generativeai` and added `google-genai` and `google-auth-oauthlib` to `pyproject.toml`. Bumped version to v2.0.6. Synchronized `opencore/__init__.py` and `frontend/package.json`.

## 2026-02-24 - Project Version Synchronization (v2.0.4)

**Observation:** Detected massive version discrepancy between documented history (v0.3.1) and actual codebase/package version (v2.0.4). No intermediate git tags or changelog entries were found for the gap between 0.3.1 and 2.0.4, indicating a breakdown in the release process.
**Action:** Performed emergency synchronization. Validated system stability via test suite (all passed). Updated `CHANGELOG.md` to establish v2.0.4 as the new baseline. Synchronized `frontend/package.json` to match backend version.

## 2026-02-23 - Release v0.3.1 Critical Patch & Metadata Sync

**Observation:** The v0.3.1 release process exposed a critical `NameError` in `opencore/tools/base.py` (`shlex` not imported) which would have caused runtime failures. Additionally, `pyproject.toml` version metadata (0.1.0) was severely outdated compared to `opencore/__init__.py` (0.3.1).
**Action:** Patched the missing import and synced `pyproject.toml` as part of the release commit. Updated CI/CD validation steps to include explicit metadata checks and linting before tagging.

## 2026-02-22 - CI/CD Bypass Detected on Main Branch

**Observation:** The release process for v0.3.0 was blocked because the `main` branch contained broken tests (`NameError` due to missing `settings` import in `opencore/core/swarm.py` and `tests/test_error_handling.py`). This suggests that PR #20 ("Introduce Centralized Configuration") was merged without passing CI checks, or the checks were insufficient.
**Action:** Patched the missing imports during the release process to unblock v0.3.0. In the future, branch protection rules should be enforced to prevent merging PRs with failing tests.

## 2024-10-24 - Initializing Release Infrastructure

**Observation:** Project lacks explicit versioning, changelog, and release tracking.
**Action:** Establish v0.1.0 as the initial release. Creating `opencore/__init__.py` for version tracking and `CHANGELOG.md` for release notes.
