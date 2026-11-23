# PathProof project brief

## User and problem
Frontend developers and educators publishing small static sites need to catch broken local navigation, asset paths, and fragment links before deploying. PathProof audits a built HTML directory without network access or modifying source files.

## Scope and stack
Python 3.10+ standard library CLI, deterministic terminal and JSON reports, read-only scanning, synthetic sample sites. This is a developer CLI rather than a hosted web app: no web UI, server, accounts, AI, or environment variables. No external URL requests, JavaScript rendering, CSS URL parsing, srcset, route rewrites, or HTML conformance validation.

## Skills demonstrated
Python parsing, pathlib containment, URL normalization, deterministic data reporting, CLI design, cross-platform regression tests, CI, and frontend publishing knowledge.

## Planned verified milestones
1. Working package setup (version/help smoke checks).
2. Brief and acceptance plan; public repo and draft PR before implementation.
3. HTML reference and ID extraction with parser tests.
4. Safe relative/root path resolution with boundary tests.
5. Deterministic site discovery and file limits with tests.
6. Missing file and fragment audit engine with fixture tests.
7. CLI summaries, exit statuses, and JSON reporting with subprocess tests.
8. Report output protection and bounded diagnostics with tests.
9. Synthetic clean/broken sample sites and end-to-end journey checks.
10. Source lint, reproducible zipapp build, and cross-platform GitHub CI.
11. Documentation, usage examples, and acceptance evidence; final checks and ready PR.
Each milestone is committed only after its checks pass. Add corrective commits for discovered issues.

## Acceptance checklist
- [ ] Scan UTF-8 .html/.htm files in a supplied directory without changing inputs.
- [ ] Check href/src local files and HTML fragments, with line numbers and actionable codes.
- [ ] Support relative paths, root paths, directory index.html, percent-encoding, and query strings.
- [ ] Skip external/special URLs explicitly, never contact the network.
- [ ] Reject links escaping the root and do not follow symlinks out of it.
- [ ] Deterministic terminal/JSON output; 0 clean, 1 findings, 2 invocation/read/write error.
- [ ] Bounded file sizes/counts and explicit incomplete-audit errors.
- [ ] JSON file output never overwrites existing files or source HTML.
- [ ] Clean and broken synthetic samples, tests, lint, build, CI, setup docs and limitations.
- [ ] At least ten focused verified commits, feature branch only after setup, same draft PR marked ready after passing checks.
