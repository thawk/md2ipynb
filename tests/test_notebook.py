import unittest

from md2ipynb.blocks import CodeBlock, MarkdownBlock
from md2ipynb.notebook import DEFAULT_METADATA, build_notebook


class BuildNotebookTests(unittest.TestCase):
    def test_python_block_becomes_code_cell(self):
        notebook = build_notebook([CodeBlock("python", ("print(1)", "print(2)"))])
        cell = notebook["cells"][0]
        self.assertEqual(cell["cell_type"], "code")
        self.assertIsNone(cell["execution_count"])
        self.assertEqual(cell["outputs"], [])
        self.assertEqual(cell["metadata"], {})
        self.assertEqual(cell["source"], ["print(1)\n", "print(2)"])

    def test_python_aliases_are_code(self):
        for language in ("python", "py", "python3", "PYTHON"):
            notebook = build_notebook([CodeBlock(language.lower(), ("x = 1",))])
            self.assertEqual(notebook["cells"][0]["cell_type"], "code", language)

    def test_non_python_block_stays_markdown_fence(self):
        notebook = build_notebook([CodeBlock("bash", ("bash run.sh",))])
        cell = notebook["cells"][0]
        self.assertEqual(cell["cell_type"], "markdown")
        self.assertEqual(cell["source"], ["```bash\n", "bash run.sh\n", "```"])

    def test_empty_language_fence(self):
        notebook = build_notebook([CodeBlock("", ("raw",))])
        self.assertEqual(notebook["cells"][0]["source"], ["```\n", "raw\n", "```"])

    def test_python_reference_stays_markdown(self):
        notebook = build_notebook([CodeBlock("python-reference", ("x = 1",))])
        self.assertEqual(notebook["cells"][0]["cell_type"], "markdown")

    def test_markdown_block_kept(self):
        notebook = build_notebook([MarkdownBlock(("# 标题", "", "正文"))])
        cell = notebook["cells"][0]
        self.assertEqual(cell["cell_type"], "markdown")
        self.assertEqual(cell["source"], ["# 标题\n", "\n", "正文"])

    def test_ids_are_unique(self):
        notebook = build_notebook(
            [MarkdownBlock(("a",)), CodeBlock("python", ("b = 1",))]
        )
        ids = [cell["id"] for cell in notebook["cells"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_id_factory_is_used(self):
        notebook = build_notebook(
            [MarkdownBlock(("a",)), MarkdownBlock(("b",))],
            id_factory=iter(["cell-1", "cell-2"]).__next__,
        )
        self.assertEqual([cell["id"] for cell in notebook["cells"]], ["cell-1", "cell-2"])

    def test_nbformat_versions(self):
        notebook = build_notebook([])
        self.assertEqual(notebook["nbformat"], 4)
        self.assertEqual(notebook["nbformat_minor"], 5)

    def test_default_metadata_is_copied(self):
        first = build_notebook([])
        first["metadata"]["kernelspec"]["display_name"] = "changed"
        second = build_notebook([])
        self.assertEqual(second["metadata"], DEFAULT_METADATA)

    def test_custom_metadata(self):
        notebook = build_notebook([], metadata={"kernelspec": {"name": "python3"}})
        self.assertEqual(notebook["metadata"], {"kernelspec": {"name": "python3"}})

    def test_empty_block_source(self):
        notebook = build_notebook([MarkdownBlock(())])
        self.assertEqual(notebook["cells"][0]["source"], [])


if __name__ == "__main__":
    unittest.main()
