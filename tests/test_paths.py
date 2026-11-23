import tempfile
import unittest
from pathlib import Path

from pathproof.paths import exact_file, resolve_reference


class PathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "guide").mkdir()
        self.source = self.root / "guide" / "index.html"
        self.source.write_text("ok", encoding="utf-8")

    def test_relative_root_encoded_query_and_fragment(self):
        result = resolve_reference(self.root, self.source, "../a%20b.html?x=1#hello%20there")
        self.assertEqual(result.path, self.root / "a b.html")
        self.assertEqual(result.fragment, "hello there")
        self.assertEqual(resolve_reference(self.root, self.source, "/guide/").path, self.source)
        self.assertEqual(resolve_reference(self.root, self.source, "#here").path, self.source)

    def test_external_and_special_urls_are_skipped(self):
        for value in ["https://example.org/x", "//cdn.example/x", "mailto:a@b", "data:image/png;base64,x", "javascript:void(0)"]:
            self.assertTrue(resolve_reference(self.root, self.source, value).skipped)

    def test_escape_and_invalid_values(self):
        for value in ["../../outside.html", "/%2e%2e/outside.html"]:
            self.assertEqual(resolve_reference(self.root, self.source, value).error, "outside-root")
        for value in ["x%GG", "x%00.html", "x\\foo", "x\nfoo", "/C:/file"]:
            self.assertEqual(resolve_reference(self.root, self.source, value).error, "invalid-url")

    def test_case_sensitive_files(self):
        self.assertTrue(exact_file(self.source, self.root))
        self.assertFalse(exact_file(self.root / "guide" / "INDEX.html", self.root))

    def test_symlinks_are_not_followed(self):
        alias = self.root / "alias"
        try:
            alias.symlink_to(self.root / "guide", target_is_directory=True)
        except OSError:
            self.skipTest("OS does not permit creating symlinks")
        self.assertEqual(resolve_reference(self.root, self.source, "/alias/index.html").error, "symlink-target")
