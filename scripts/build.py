"""Build a reproducible dependency-free zipapp and exercise packaged journeys."""
import io
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
    sources = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8").encode("utf-8") for p in sorted((ROOT / "pathproof").glob("*.py"))}
    sources["__main__.py"] = b"from pathproof.__main__ import main\nraise SystemExit(main())\n"
    for name, data in sorted(sources.items()):
        info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        info.external_attr = 0o644 << 16
        archive.writestr(info, data)
output = ROOT / "dist" / "pathproof.pyz"
output.parent.mkdir(exist_ok=True)
output.write_bytes(buffer.getvalue())
for sample, expected in [("clean", 0), ("broken", 1)]:
    result = subprocess.run([sys.executable, str(output), str(ROOT / "examples" / sample)], capture_output=True, text=True, cwd=output.parent)
    if result.returncode != expected:
        raise SystemExit(f"Packaged {sample} journey failed: {result.stdout} {result.stderr}")
print(f"Built {output.relative_to(ROOT)} ({output.stat().st_size} bytes); packaged clean/broken journeys passed.")
