"""Combine parsed documents into a deterministic audit report."""
from dataclasses import asdict, dataclass, field

from .paths import exact_file, resolve_reference
from .scan import HTML_SUFFIXES, scan_site

MESSAGES = {
    "missing-file": "Create the target file or correct its path/case.",
    "missing-fragment": "Add the target ID or correct the fragment (IDs are case-sensitive).",
    "outside-root": "Keep the target inside the supplied site directory.",
    "invalid-url": "Use a valid URL path with forward slashes and valid percent-encoding.",
    "symlink-target": "Use an ordinary file inside the site directory, not a symlink.",
    "duplicate-id": "Give each element a unique ID.",
    "unsupported-base": "Remove base href or audit a build with explicit paths; this page's links were not checked.",
    "unreadable-target": "Fix the target HTML read error before trusting its fragment checks.",
}


@dataclass
class Finding:
    source: str
    line: int
    code: str
    target: str
    message: str


@dataclass
class Report:
    files: int = 0
    checked: int = 0
    skipped: int = 0
    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def exit_code(self):
        return 2 if self.errors else (1 if self.findings else 0)

    def to_dict(self):
        return {"schema_version": 1, "complete": not self.errors, **asdict(self), "exit_code": self.exit_code}


def audit(directory, max_references=50_000):
    scan = scan_site(directory)
    report = Report(files=len(scan.documents), errors=list(scan.errors))

    def finding(source, line, code, value):
        if len(report.findings) < 5000:
            report.findings.append(Finding(source, line, code, value, MESSAGES[code]))
        elif "Finding limit reached; only the first 5000 findings retained." not in report.errors:
            report.errors.append("Finding limit reached; only the first 5000 findings retained.")

    for path, document in sorted(scan.documents.items()):
        source = path.relative_to(scan.root).as_posix()
        for value, line in document.duplicate_ids:
            finding(source, line, "duplicate-id", value)
        if document.has_base:
            finding(source, 1, "unsupported-base", "base href")
            report.errors.append(f"Links not checked because of base href: {source}")
            continue
        for reference in document.references:
            if report.checked + report.skipped >= max_references:
                report.errors.append(f"Site exceeds the {max_references}-reference limit.")
                return report
            target = resolve_reference(scan.root, path, reference.value)
            if target.skipped:
                report.skipped += 1
                continue
            report.checked += 1
            code = target.error
            if not code:
                try:
                    if not exact_file(target.path, scan.root):
                        code = "missing-file"
                    elif target.fragment and target.path.suffix.lower() in HTML_SUFFIXES:
                        destination = scan.documents.get(target.path)
                        if destination is None:
                            code = "unreadable-target"
                            report.errors.append(f"Target HTML not scanned: {target.path.relative_to(scan.root).as_posix()}")
                        elif target.fragment not in destination.ids and target.fragment.lower() != "top":
                            code = "missing-fragment"
                except OSError:
                    report.errors.append(f"Cannot inspect target for {source}:{reference.line}")
            if code:
                finding(source, reference.line, code, reference.value)
    report.findings.sort(key=lambda f: (f.source, f.line, f.code, f.target))
    return report
