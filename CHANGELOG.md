# Changelog

All notable changes to this project are documented in this file.

## [0.1.1] - 2026-11-08

### Fixed

- `decide` no longer returns `defer` with `retry_after=0.0` when the pending
  wait is exactly `max_defer_seconds`; that boundary is now treated as a
  timeout.
- A non-monotonic `now` (earlier than `received_at`) can no longer produce a
  deferral longer than `max_defer_seconds`.
- CI no longer fails on Python 3.9. The 3.9 job is pinned to `ubuntu-22.04`,
  because `ubuntu-latest` no longer provides a 3.9 build.

### Added

- `[project.urls]`: Homepage, Repository, Issues, Changelog.
- Python 3.9–3.13 and Development Status classifiers.
- Top-level re-exports, so `from mm_preprocess_kit import decide` works.

### Changed

- README and README.zh-CN language links now use absolute URLs, so they also
  work on PyPI.
- Python 3.9 and 3.10 are no longer supported: both are end-of-life, and
  their `setup-python` downloads fail with HTTP 504 on hosted runners.
  `requires-python` is now `>=3.11`.

## [0.1.0] - 2026-11-06

### Added

- Initial release: caption retry, pending-message deferral, caption-mode
  selection, and safe fallback policies.
