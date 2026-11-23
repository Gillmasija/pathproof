import tempfile
import unittest
from pathlib import Path

from pathproof.audit import audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, html):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    def test_clean_cross_page_assets_and_skips(self):
        self.write("index.html", '<a href="guide/?v=1#intro">Go</a><img src="a.svg"><a href="https://example.org">External</a>')
        self.write("guide/index.html", '<h1 id="intro">Guide</h1><a href="/index.html">Home</a>')
        self.write("a.svg", '<svg/>')
        result = audit(self.root)
        self.assertEqual((result.files, result.checked, result.skipped, result.exit_code), (2, 3, 1, 0))

    def test_broken_file_anchor_escape_and_duplicate(self):
        self.write("index.html", '<p id="a"></p><p id="a"></p>\n<a href="#b">B</a>\n<img src="missing.png"><a href="../out.html">Out</a>')
        result = audit(self.root)
        self.assertEqual([f.code for f in result.findings], ["duplicate-id", "missing-fragment", "missing-file", "outside-root"])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.to_dict(), audit(self.root).to_dict())

    def test_base_marks_incomplete_and_limits_are_errors(self):
        self.write("index.html", '<base href="/foo/"><a href="no">No</a>')
        self.assertEqual(audit(self.root).exit_code, 2)
        self.write("index.html", '<a href="#">A</a><a href="#">B</a>')
        self.assertEqual(audit(self.root, max_references=1).exit_code, 2)

    def test_no_fragment_claim_for_binary_and_utf8_failure(self):
        self.write("index.html", '<a href="manual.pdf#page=1">PDF</a><a href="bad.html#x">Bad</a>')
        self.write("manual.pdf", 'synthetic placeholder')
        (self.root / "bad.html").write_bytes(b"\xff")
        result = audit(self.root)
        self.assertEqual([f.code for f in result.findings], ["unreadable-target"])
        self.assertFalse(result.to_dict()["complete"])

    def test_browser_top_fragment_and_finding_limit(self):
        self.write("index.html", '<a href="#top">Top</a><a href="#TOP">Top</a>')
        self.assertEqual(audit(self.root).exit_code, 0)
        self.write("index.html", '<a href="missing">Missing</a>' * 5001)
        result = audit(self.root)
        self.assertEqual(len(result.findings), 5000)
        self.assertEqual(result.exit_code, 2)
