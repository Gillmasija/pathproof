import hashlib
import unittest
from pathlib import Path

from pathproof.audit import audit

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ExampleTests(unittest.TestCase):
    def test_clean_journey_and_source_preservation(self):
        paths = sorted(p for p in EXAMPLES.rglob("*") if p.is_file())
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        clean = audit(EXAMPLES / "clean")
        self.assertEqual((clean.exit_code, clean.files, clean.checked, clean.skipped), (0, 2, 5, 1))
        broken = audit(EXAMPLES / "broken")
        self.assertEqual(broken.exit_code, 1)
        self.assertEqual([f.line for f in broken.findings], [6, 7, 8, 9])
        self.assertEqual([f.code for f in broken.findings], ["missing-file", "missing-fragment", "missing-file", "outside-root"])
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
