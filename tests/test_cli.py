import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "pathproof", str(self.root), *args], capture_output=True, text=True)

    def test_clean_and_findings_exit_statuses(self):
        path = self.root / "index.html"
        path.write_text('<h1 id="x">Hi</h1><a href="#x">X</a>', encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CLEAN:", result.stdout)
        path.write_text('<a href="missing.html">Missing</a>', encoding="utf-8")
        result = self.run_cli("--format", "json")
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertEqual(data["findings"][0]["source"], "index.html")
        self.assertEqual(data["findings"][0]["code"], "missing-file")
        self.assertTrue(data["complete"])

    def test_empty_directory_and_invalid_arguments(self):
        result = self.run_cli("--format", "json")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["complete"])
        self.assertEqual(self.run_cli("--format", "xml").returncode, 2)
