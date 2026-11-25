"""Command entry point."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .audit import audit


def terminal_report(report):
    lines = [f"PathProof: {report.files} HTML files | {report.checked} local references | {report.skipped} external/special URLs skipped"]
    for item in report.findings[:100]:
        lines.append(f"{item.source}:{item.line} [{item.code}] {item.target[:240]!r}\n  {item.message}")
    if len(report.findings) > 100:
        lines.append("Showing first 100 findings; use --format json for all retained findings.")
    lines.extend(f"ERROR: {error}" for error in report.errors)
    status = "INCOMPLETE" if report.errors else ("FINDINGS" if report.findings else "CLEAN")
    lines.append(f"{status}: {len(report.findings)} findings, {len(report.errors)} errors. External URLs were not tested.")
    return "\n".join("".join(c if ord(c) >= 32 and ord(c) != 127 or c == "\n" else repr(c)[1:-1] for c in line) for line in lines)


def main():
    parser = argparse.ArgumentParser(prog="pathproof", description="Offline static HTML link checker")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("directory", help="Built site directory containing .html/.htm files")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", type=Path, help="Create a NEW .json report file (requires --format json)")
    args = parser.parse_args()
    if args.output and (args.format != "json" or args.output.suffix.lower() != ".json"):
        parser.error("--output requires --format json and a .json filename")
    try:
        report = audit(args.directory)
        output = json.dumps(report.to_dict(), indent=2, ensure_ascii=True) if args.format == "json" else terminal_report(report)
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(output + "\n")
            print(f"Created report: {args.output}", file=sys.stderr)
        else:
            print(output)
        return report.exit_code
    except (OSError, ValueError, RuntimeError) as error:
        print(f"PathProof error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
