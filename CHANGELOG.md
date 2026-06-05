# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 2026-06-05

### Added
- pydantic-settings CLI: `--profiles`, `--active_profile`, `--reuse_connection`, `--settle_seconds` (also `G600_*` env vars).
- Optional connection reuse: open the device once and reuse the handle for all operations (off by default).
- `justfile` with `format`, `lint`, `lint-fix`, `check`, and `run` recipes.
- ruff dev dependency and lint/format config in `pyproject.toml`.

### Changed
- Write all 3 profiles in one run and exit, instead of an infinite interactive prompt loop.
- Leave profile 0 (the only fully configured profile) as the active profile after writing.
- Raise on device errors instead of calling `sys.exit()` mid-method; exit with a non-zero status on failure.
- Guard execution behind `if __name__ == "__main__"` so the module can be imported without touching the device.
- Collapse the repetitive `__str__` button listing into loops.
- Replace the four `dpi1`-`dpi4` property pairs with `get_dpi`/`set_dpi`.

### Fixed
- Close the device handle on the write error path (was leaking).
- Check the return value when setting the active profile.
- Correct the `frequency` setter return type annotation (`None`).

### Removed
- Dead commented-out button mappings and a misleading Play/Pause comment.
- Dead/broken `left_click` property (read an uninitialized attribute).
