"""Command entry point."""
import argparse
import json
import sys

from . import __version__
from .audit import audit


def terminal_report(report):
    lines = [f"PathProof: {report.files} HTML files | {report.checked} local references | {report.skipped} external/special URLs skipped"]
    for item in report.findings:
        lines.append(f"{item.source}:{item.line} [{item.code}] {item.target!r}\n  {item.message}")
    lines.extend(f"ERROR: {error}" for error in report.errors)
    status = "INCOMPLETE" if report.errors else ("FINDINGS" if report.findings else "CLEAN")
    lines.append(f"{status}: {len(report.findings)} findings, {len(report.errors)} errors. External URLs were not tested.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Offline static HTML link checker")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("directory", help="Built site directory containing .html/.htm files")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    try:
        report = audit(args.directory)
        output = json.dumps(report.to_dict(), indent=2, ensure_ascii=True) if args.format == "json" else terminal_report(report)
        print(output)
        return report.exit_code
    except (OSError, ValueError, RuntimeError) as error:
        print(f"PathProof error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
