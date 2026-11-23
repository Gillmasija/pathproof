import unittest

from pathproof.parser import parse_html


class ParserTests(unittest.TestCase):
    def test_lines_entities_and_self_closing_assets(self):
        doc = parse_html('<h1 id="a">Hi</h1>\n<a href="x?a=1&amp;b=2">X</a><img src="a.png"/>')
        self.assertEqual(doc.ids, {"a"})
        self.assertEqual([(r.value, r.line) for r in doc.references], [("x?a=1&b=2", 2), ("a.png", 2)])

    def test_comments_script_and_legacy_anchor(self):
        doc = parse_html('<!-- <a href="no"> --><script>"<a href=bad>"</script><a name="old"></a>')
        self.assertEqual(doc.references, [])
        self.assertEqual(doc.ids, {"old"})

    def test_base_and_duplicate_ids(self):
        doc = parse_html('<base href="/site/"><p id="x"></p>\n<p id="x">')
        self.assertTrue(doc.has_base)
        self.assertEqual(doc.duplicate_ids, [("x", 2)])
