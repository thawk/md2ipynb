import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from md2ipynb.cli import main

SAMPLE = """# 标题

正文。

```python
print("hi")
```
"""


def run_cli(argv):
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        status = main(argv)
    return status, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.source = self.root / "01-demo.md"
        self.source.write_text(SAMPLE, encoding="utf-8")

    def test_single_file(self):
        status, stdout, stderr = run_cli([str(self.source)])
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("01-demo.ipynb", stdout)
        self.assertTrue((self.root / "01-demo.ipynb").is_file())

    def test_multiple_files(self):
        second = self.root / "02-demo.md"
        second.write_text("# 二\n", encoding="utf-8")
        status, stdout, _ = run_cli([str(self.source), str(second)])
        self.assertEqual(status, 0)
        self.assertIn("01-demo.ipynb", stdout)
        self.assertIn("02-demo.ipynb", stdout)
        self.assertTrue((self.root / "02-demo.ipynb").is_file())

    def test_output_dir(self):
        target = self.root / "notebooks"
        status, _, _ = run_cli(["-o", str(target), str(self.source)])
        self.assertEqual(status, 0)
        self.assertTrue((target / "01-demo.ipynb").is_file())

    def test_existing_file_is_skipped(self):
        run_cli([str(self.source)])
        output = self.root / "01-demo.ipynb"
        output.write_text("marker", encoding="utf-8")
        status, _, stderr = run_cli([str(self.source)])
        self.assertEqual(status, 0)
        self.assertIn("跳过", stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "marker")

    def test_force_overwrites(self):
        run_cli([str(self.source)])
        output = self.root / "01-demo.ipynb"
        output.write_text("marker", encoding="utf-8")
        status, _, _ = run_cli(["-f", str(self.source)])
        self.assertEqual(status, 0)
        notebook = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(notebook["nbformat"], 4)

    def test_missing_file_returns_error(self):
        status, _, stderr = run_cli([str(self.root / "missing.md")])
        self.assertEqual(status, 1)
        self.assertIn("错误", stderr)

    def test_unclosed_fence_returns_error(self):
        broken = self.root / "broken.md"
        broken.write_text("```python\nx = 1\n", encoding="utf-8")
        status, _, stderr = run_cli([str(broken)])
        self.assertEqual(status, 1)
        self.assertIn("围栏", stderr)

    def test_quiet_silences_success(self):
        status, stdout, _ = run_cli(["-q", str(self.source)])
        self.assertEqual(status, 0)
        self.assertEqual(stdout, "")

    def test_version_exits_zero(self):
        with self.assertRaises(SystemExit) as caught:
            run_cli(["-V"])
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
