"""Bounded deterministic discovery of UTF-8 HTML documents."""
import os
from dataclasses import dataclass, field
from pathlib import Path

from .parser import Document, parse_html

IGNORED = {".git", "node_modules", ".venv", "__pycache__"}
HTML_SUFFIXES = {".html", ".htm"}


@dataclass
class Scan:
    root: Path
    documents: dict[Path, Document] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def scan_site(directory, max_files=2000, max_bytes=1_000_000, max_total=32_000_000):
    root = Path(directory).resolve()
    result = Scan(root)
    if not root.is_dir():
        result.errors.append("Site root must be an existing directory.")
        return result
    total = count = entries = 0

    def walk_error(error):
        result.errors.append(f"Cannot list directory: {error.filename}")

    for parent, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        entries += len(dirs) + len(files)
        if entries > 20_000:
            result.errors.append("Site exceeds the 20000-entry discovery limit.")
            break
        dirs[:] = sorted(d for d in dirs if d not in IGNORED)
        for name in dirs[:]:
            path = Path(parent) / name
            if path.is_symlink():
                result.errors.append(f"Symlink directory not scanned: {path.relative_to(root).as_posix()}")
                dirs.remove(name)
        for name in sorted(files):
            path = Path(parent) / name
            if path.suffix.lower() not in HTML_SUFFIXES:
                continue
            relative = path.relative_to(root).as_posix()
            count += 1
            if count > max_files:
                result.errors.append(f"Site exceeds the {max_files}-HTML-file limit.")
                return result
            if path.is_symlink():
                result.errors.append(f"Symlink HTML not scanned: {relative}")
                continue
            try:
                with path.open("rb") as stream:
                    data = stream.read(max_bytes + 1)
                total += len(data)
                if len(data) > max_bytes:
                    result.errors.append(f"HTML exceeds {max_bytes} bytes: {relative}")
                    continue
                if total > max_total:
                    result.errors.append(f"HTML input exceeds {max_total} total bytes.")
                    return result
                result.documents[path] = parse_html(data.decode("utf-8-sig"))
            except (OSError, ValueError) as error:
                result.errors.append(f"Cannot read UTF-8 HTML: {relative} ({type(error).__name__})")
    if not result.documents and not result.errors:
        result.errors.append("No .html or .htm files found in the site root.")
    return result
