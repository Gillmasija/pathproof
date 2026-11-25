import tempfile
import os
import unittest
from pathlib import Path

from pathproof.scan import scan_site


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_empty_missing_and_invalid_encoding(self):
        self.assertTrue(scan_site(self.root).errors)
        self.assertTrue(scan_site(self.root / "missing").errors)
        (self.root / "bad.html").write_bytes(b"\xff")
        self.assertIn("UTF-8", scan_site(self.root).errors[0])

    def test_bom_sorted_files_and_ignored_dependencies(self):
        for name in ["b.htm", "a.html"]:
            (self.root / name).write_bytes(b'\xef\xbb\xbf<p id="yes">')
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "bad.html").write_bytes(b"\xff")
        scan = scan_site(self.root)
        self.assertEqual([p.name for p in scan.documents], ["a.html", "b.htm"])
        self.assertEqual(scan.errors, [])
        self.assertEqual(next(iter(scan.documents.values())).ids, {"yes"})

    def test_file_size_count_and_total_limits(self):
        (self.root / "a.html").write_text("12345", encoding="utf-8")
        (self.root / "b.html").write_text("12345", encoding="utf-8")
        self.assertIn("bytes", scan_site(self.root, max_bytes=4).errors[0])
        self.assertIn("file limit", scan_site(self.root, max_files=1).errors[0])
        self.assertIn("total bytes", scan_site(self.root, max_total=9).errors[0])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes require POSIX")
    def test_named_pipe_is_rejected_without_reading(self):
        os.mkfifo(self.root / "pipe.html")
        self.assertIn("Non-regular", scan_site(self.root).errors[0])

    def test_symlink_directory_is_not_traversed(self):
        (self.root / "index.html").write_text("ok", encoding="utf-8")
        try:
            (self.root / "loop").symlink_to(self.root, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not permit creating symlinks")
        scan = scan_site(self.root)
        self.assertEqual(len(scan.documents), 1)
        self.assertIn("Symlink directory", scan.errors[0])
