# Verification

## Local results — 2026-11-23

- Python 3.10: 26 tests discovered; 23 pass, 3 OS-dependent skips, 0 failures.
  Windows disallows symlink creation here (two tests); named pipes require POSIX
  (one test). The Ubuntu CI jobs run those cases without these restrictions.
- `python scripts/lint.py`: passes syntax and source-hygiene checks, 14 files.
- `python scripts/build.py`: creates `dist/pathproof.pyz`; packaged clean and
  broken journeys pass from the dist working directory.
- `git diff --check`: passes.
- Synthetic clean sample: 2 HTML files, 5 local references, 1 skipped external
  link, 0 findings, exit 0. Broken sample: 4 expected findings, exit 1.
- Read-only check of the existing SessionMap build: 3 HTML files, 27 local
  references, 0 findings, exit 0. This does not test the site's browser behavior.
- Regression tests verify source hashes remain unchanged, JSON files cannot be
  overwritten, case sensitivity on Windows, invalid UTF-8, traversal, bounds,
  incomplete scans, base href rejection, duplicate IDs, and repeatable reports.
- Repeated-link caching reduced the local suite from about 20 seconds to about
  3 seconds while retaining every finding's original line number.

The GitHub matrix runs the same checks on Windows/Ubuntu with Python 3.10/3.13.
All final-head CI jobs must succeed before this draft PR is marked ready.

## What was not claimed

No web UI or deployment is needed for this offline CLI, so browser screenshots
would not demonstrate its main journey. The README includes actual terminal
output instead. No external links were probed; no production site was modified.
The tool is not an HTML validator, crawler, security scanner, or browser renderer.
Supported checks and explicit limits are listed in the README.
