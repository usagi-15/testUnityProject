import json
import tempfile
import unittest
from pathlib import Path

from exhibition.builder import CONTENT_DIR, build, load_works


class BuildTest(unittest.TestCase):
    def test_build_generates_all_pages(self):
        works = load_works()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            written = build(out)
            self.assertEqual(len(written), len(works) + 1)
            index = (out / "index.html").read_text(encoding="utf-8")
            for w in works:
                self.assertIn(f'href="works/{w.id}.html"', index)
                self.assertTrue((out / "works" / f"{w.id}.html").exists())
            self.assertTrue((out / "style.css").exists())
            self.assertTrue((out / "main.js").exists())

    def test_html_is_escaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            content.mkdir()
            (content / "site.json").write_text((CONTENT_DIR / "site.json").read_text(encoding="utf-8"), encoding="utf-8")
            work = {"id": "x", "title": "<script>alert(1)</script>", "artist": "A", "year": 2026,
                    "category": "絵画", "description": "d"}
            (content / "works.json").write_text(json.dumps([work]), encoding="utf-8")
            out = Path(tmp) / "dist"
            build(out, content_dir=content)
            html = (out / "works" / "x.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", html)
            self.assertIn("&lt;script&gt;", html)

    def test_missing_field_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp)
            (content / "works.json").write_text(json.dumps([{"id": "x"}]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_works(content)

    def test_duplicate_id_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp)
            w = {"id": "x", "title": "t", "artist": "a", "year": 1, "category": "c", "description": "d"}
            (content / "works.json").write_text(json.dumps([w, w]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_works(content)


if __name__ == "__main__":
    unittest.main()
