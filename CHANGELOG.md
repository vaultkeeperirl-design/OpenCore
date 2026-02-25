# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.3] - 2026-02-25

### Fixed
- **Security**: Fixed unrestricted file upload in `/transcribe` endpoint (PR #126).
- Enforced file size limits and extension validation for audio uploads.

## [2.1.2] - 2026-02-25

### Skipped
- Internal release / Validation failure.

## [2.1.1] - 2026-02-25

### Skipped
- Internal release / Validation failure.

## [2.1.0] - 2026-02-24

### Added
- **Theme Manager**: New UI feature allowing users to switch between 6 persistent themes (Cyberpunk, Dark Cool, Forest, Corporate Light, Warm Light, Lavender Light).
- **Theme Persistence**: Selected theme is saved to local storage and automatically applied on visit.
- **Frontend UI Refresh**: Updated frontend build artifacts to include the latest UI components and accessibility improvements.

## [2.0.6] - 2026-02-24

### Fixed
- Fixed startup crash due to missing `google-auth-oauthlib` dependency.
- Updated `pyproject.toml` to replace `google-generativeai` with `google-genai`.

## [2.0.4] - 2026-02-24

### Changed
- **Release Baseline**: Synchronized project version to v2.0.4 to address undocumented version gap.
- Updated `frontend/package.json` to match backend version.
- Verified system stability with full regression test suite.

## [0.3.1] - 2026-02-22

### Fixed
- Security vulnerability in file tools preventing path traversal.

## [0.3.0] - 2026-02-22

### Changed
- Introduce Centralized Configuration (Merge PR #20).

## [0.2.0] - 2026-02-21

### Changed
- Palette Accessibility Improvements (Merge PR #15).

## [0.1.0] - 2024-10-24

### Added
- Initial project release.
- Added `opencore/__init__.py` for package versioning.
- Added `.Jules/conductor.md` for release journaling.
- Added `CHANGELOG.md` to track project history.

### Changed
- Refined agent think tool extraction logic (Merge PR #8).
