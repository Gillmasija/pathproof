"""Dependency-free source syntax and whitespace checks."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = sorted(p for folder in ["pathproof", "scripts", "tests"] for p in (ROOT / folder).rglob("*.py"))
for path in files:
    text = path.read_text(encoding="utf-8")
    ast.parse(text, filename=str(path))
    for number, line in enumerate(text.splitlines(), 1):
        if line != line.rstrip() or "\t" in line or line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            raise SystemExit(f"Source hygiene error: {path.relative_to(ROOT)}:{number}")
print(f"Lint passed: Python syntax and source hygiene ({len(files)} files).")
