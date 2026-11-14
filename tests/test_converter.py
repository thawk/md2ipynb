import json
import re
import tempfile
import unittest
from pathlib import Path

from md2ipynb.converter import (
    OutputExistsError,
    convert_file,
    convert_text,
    write_notebook,
)

SAMPLE = """# 示例

正文第一段。

| 环节 | 说明 |
| --- | --- |
| 一 | 二 |

```python
print("你好")
```

```bash
bash run.sh
```

```python-reference
x = 1
```
"""


def content_lines(lines):
    """去掉空行与围栏行，只比较实际内容。"""
    return [
        line.strip()
        for line in lines
        if line.strip() and not re.match(r"^\s*```", line)
    ]


def notebook_lines(notebook):
    lines = []
    for cell in notebook["cells"]:
        source = "".join(cell["source"]).splitlines()
        if cell["cell_type"] == "code":
            lines += ["```python", *source, "```"]
        else:
            lines += source
    return lines


class ConvertTextTests(unittest.TestCase):
    def test_cell_types(self):
        notebook = convert_text(SAMPLE)
        self.assertEqual(
            [cell["cell_type"] for cell in notebook["cells"]],
            ["markdown", "code", "markdown", "markdown"],
        )

    def test_content_roundtrip(self):
        notebook = convert_text(SAMPLE)
        self.assertEqual(
            content_lines(SAMPLE.splitlines()),
            content_lines(notebook_lines(notebook)),
        )

    def test_metadata_override(self):
        notebook = convert_text("# 标题\n", metadata={"custom": True})
        self.assertEqual(notebook["metadata"], {"custom": True})

    def test_id_factory(self):
        notebook = convert_text("# 标题\n", id_factory=iter(["only"]).__next__)
        self.assertEqual(notebook["cells"][0]["id"], "only")


class ConvertFileTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.source = self.root / "01-demo.md"
        self.source.write_text(SAMPLE, encoding="utf-8")

    def test_writes_next_to_source(self):
        result = convert_file(self.source)
        self.assertEqual(result.output, self.root / "01-demo.ipynb")
        self.assertTrue(result.output.is_file())

    def test_written_file_is_notebook_json(self):
        result = convert_file(self.source)
        notebook = json.loads(result.output.read_text(encoding="utf-8"))
        self.assertEqual(notebook["nbformat"], 4)
        self.assertIn("你好", result.output.read_text(encoding="utf-8"))

    def test_counts(self):
        result = convert_file(self.source)
        self.assertEqual(result.code_cells, 1)
        self.assertEqual(result.markdown_cells, 3)
        self.assertEqual(result.total_cells, 4)

    def test_output_dir_created(self):
        target = self.root / "nested" / "notebooks"
        result = convert_file(self.source, output_dir=target)
        self.assertEqual(result.output, target / "01-demo.ipynb")
        self.assertTrue(result.output.is_file())

    def test_explicit_output(self):
        target = self.root / "custom.ipynb"
        result = convert_file(self.source, output=target)
        self.assertEqual(result.output, target)

    def test_output_and_output_dir_conflict(self):
        with self.assertRaises(ValueError):
            convert_file(self.source, output="a.ipynb", output_dir="b")

    def test_existing_file_raises(self):
        result = convert_file(self.source)
        result.output.write_text("marker", encoding="utf-8")
        with self.assertRaises(OutputExistsError) as caught:
            convert_file(self.source)
        self.assertEqual(caught.exception.path, result.output)
        self.assertEqual(result.output.read_text(encoding="utf-8"), "marker")

    def test_overwrite(self):
        result = convert_file(self.source)
        result.output.write_text("marker", encoding="utf-8")
        convert_file(self.source, overwrite=True)
        self.assertNotEqual(result.output.read_text(encoding="utf-8"), "marker")

    def test_missing_source(self):
        with self.assertRaises(FileNotFoundError):
            convert_file(self.root / "missing.md")

    def test_write_notebook(self):
        target = self.root / "direct.ipynb"
        write_notebook(convert_text("# 标题\n"), target)
        self.assertTrue(target.is_file())


if __name__ == "__main__":
    unittest.main()
