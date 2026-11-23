"""Conservative URL to local-file resolution."""
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class Target:
    path: Path | None = None
    fragment: str = ""
    skipped: bool = False
    error: str = ""


def resolve_reference(root, source, value):
    value = value.strip()
    if any(ord(c) < 32 for c in value) or "\\" in value:
        return Target(error="invalid-url")
    try:
        url = urlsplit(value)
        if url.scheme or url.netloc or value.startswith("//"):
            return Target(skipped=True)
        if re.search(r"%(?![0-9a-fA-F]{2})", url.path + url.fragment):
            return Target(error="invalid-url")
        path = unquote(url.path, errors="strict")
        fragment = unquote(url.fragment, errors="strict")
        if any(ord(c) < 32 for c in path + fragment) or "\\" in path or ":" in path:
            return Target(error="invalid-url")
        candidate = (root / path.lstrip("/")) if path.startswith("/") else (source.parent / path if path else source)
        # Inspect before resolve(), which would erase evidence of symlink traversal.
        if candidate.is_symlink() or any(p.is_symlink() for p in candidate.parents if p != root):
            return Target(error="symlink-target")
        candidate = candidate.resolve()
        candidate.relative_to(root)
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if candidate.is_symlink():
            return Target(error="symlink-target")
        return Target(candidate, fragment)
    except (ValueError, OSError, RuntimeError):
        return Target(error="outside-root")


def exact_file(path, root):
    """Honor URL path case even on a case-insensitive Windows filesystem."""
    parent = root
    for part in path.relative_to(root).parts:
        if not parent.is_dir() or part not in {p.name for p in parent.iterdir()}:
            return False
        parent = parent / part
    return parent.is_file()
