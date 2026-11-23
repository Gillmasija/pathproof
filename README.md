# PathProof

Catch broken local navigation before publishing a static site. PathProof checks a
built HTML directory for missing pages, assets, fragments, and duplicate IDs.
It runs entirely offline and never changes the site it audits.

Python 3.10+ • standard library only • Windows and Linux CI • no API keys

## Quick start

Clone this repository, open its folder, then run:

```sh
python -m pathproof examples/clean
python -m pathproof examples/broken
python -m pathproof /path/to/your/built-site
```

On Windows, quote paths containing spaces, for example:
`python -m pathproof "C:\Sites\My Portfolio\dist"`.

The clean sample returns exit code **0**. The intentionally broken sample returns
**1** and explains four problems:

```text
PathProof: 1 HTML files | 4 local references | 0 external/special URLs skipped
index.html:6 [missing-file] 'lesson.html'
  Create the target file or correct its path/case.
index.html:7 [missing-fragment] '#summary'
  Add the target ID or correct the fragment (IDs are case-sensitive).
index.html:8 [missing-file] 'missing.svg'
  Create the target file or correct its path/case.
index.html:9 [outside-root] '../outside.html'
  Keep the target inside the supplied site directory.
FINDINGS: 4 findings, 0 errors. External URLs were not tested.
```

Correct the reported target path or add the missing ID, then run the same command
again. Each result points to the opening tag's line in the source HTML.

## JSON and automation

```sh
python -m pathproof examples/broken --format json
python -m pathproof examples/clean --format json --output audit.json
```

`--output` requires a new `.json` filename. Existing files are never overwritten;
choose a new filename for a later run. A missing output parent is an error. File
output goes only to that explicit destination. Without it, the report uses stdout.

JSON schema version 1 includes `complete`, `files`, `checked`, `skipped`,
`findings`, `errors`, and `exit_code`. Findings contain `source`, `line`, `code`,
`target`, and `message`. Source paths are relative to the supplied root. A complete
report means the supported local checks finished; it makes no claim about skipped
external links or unsupported dynamic behavior. Invocation/output failures go to
stderr and may not produce a JSON report.

| Exit | Meaning |
| --- | --- |
| 0 | Supported local checks completed without findings |
| 1 | Audit completed with findings that need attention |
| 2 | Incomplete audit, invalid arguments, or a read/write/limit error |

## What gets checked

- UTF-8 (including BOM) `.html` and `.htm` documents throughout the root.
- Static `href` and `src` values, decoded HTML entities, URL query strings,
  percent-encoded paths/fragments, and relative or root-relative links.
- Directory URLs resolve to `index.html`. Root-relative links start at the
  supplied directory. File spelling is case-sensitive, including on Windows.
- Fragment IDs in HTML, legacy `<a name>` targets, and the browser's special
  `#top` target. Duplicate element IDs are reported.
- Symlink targets and paths outside the root are rejected. Symlink/redirected
  directories and non-regular HTML inputs produce incomplete-audit errors.

External URLs, protocol-relative URLs, and all URL schemes (`mailto:`, `data:`,
`javascript:`, etc.) are counted as skipped. No network request is made, and
skipping a URL is not a safety or validity endorsement.

## Limits and design decisions

This tool checks a **static build**, not a running application. JavaScript-created
navigation/IDs, SPA routes, server redirects, clean-URL rewrites, CSS `url()`,
`srcset`, iframe `srcdoc`, form actions, text fragments, and HTML conformance are
outside its scope. Fragments in non-HTML assets (PDF/SVG, for example) are not
validated. Browser URL normalization and hosting-specific decoding may differ;
check the actual deployed site as well. A document with `<base href>` is explicitly
marked incomplete instead of reporting potentially incorrect relative links.

Directories named `.git`, `node_modules`, `.venv`, and `__pycache__` are excluded.
Audit the output folder, not an entire source repository. Empty sites are errors.
Limits are 2,000 HTML files, 1,000,000 bytes per HTML file, 32,000,000 input bytes,
20,000 discovered directory entries, 20,000 extracted entries per document,
50,000 references, and 5,000 retained findings. A reached limit makes the audit
incomplete (exit 2); it never silently reports a clean result. Terminal output
shows at most 100 findings with targets shortened to 240 characters. JSON retains
the full targets for retained findings.

Checks reuse path results within one audit for speed. Do not change a site's
files while scanning. This is a developer aid for trusted build directories,
not a sandbox for hostile or concurrently modified filesystems. Reports include
your HTML's link values; review them before sharing publicly.

## Development and portable build

```sh
python -m unittest discover -s tests -v
python scripts/lint.py
python scripts/build.py
python dist/pathproof.pyz examples/clean
```

The build creates a deterministic standard-library zipapp and exercises both
sample journeys from outside the source package directory. Copy `pathproof.pyz`
to another machine with Python 3.10+ to use it. No installation, service, database,
environment variables, or `.env` file is required. CI tests Python 3.10/3.13 on
Ubuntu and Windows and uploads the zipapp as a workflow artifact.

See [the project brief](PROJECT_BRIEF.md) and [verification evidence](docs/VERIFICATION.md).
