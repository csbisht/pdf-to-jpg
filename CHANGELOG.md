# Changelog

All notable changes to this project will be documented here.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [0.2.0] - 2026-05-28

### Added
- Batch mode: pass a folder path to convert all PDFs inside it at once
- Progress bar using `tqdm` — shows live page-by-page rendering progress
- Issue templates, PR template, and community health files
- CI workflow (GitHub Actions) — lint + smoke tests on Python 3.9–3.12 across Linux, macOS, Windows
- Dependabot config for automated weekly dependency updates
- Smoke test suite (`tests/test_smoke.py`)

### Changed
- **Switched PDF engine** from PyMuPDF (AGPL v3) to `pypdfium2` (Apache 2.0)
- **License changed** from AGPL v3 to **MIT** — no restrictions on use
- `_stack_pixmaps` replaced by simpler `_stack_images` using Pillow
- Dependency pinning added — lower bounds on all three packages

### Fixed
- Copyright year updated to 2025-2026

---

## [0.1.0] - 2025-01-01

### Added
- Initial release
- Convert PDF to JPG — combined mode (all pages stacked) and per-page mode
- CLI with `--dpi`, `--quality`, `--name`, `-p` flags
- Single dependency: PyMuPDF
