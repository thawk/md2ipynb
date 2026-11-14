import unittest

from md2ipynb.blocks import CodeBlock, MarkdownBlock
from md2ipynb.parser import MarkdownParseError, parse_markdown


class ParseMarkdownTests(unittest.TestCase):
    def test_python_fence_detected(self):
        blocks = parse_markdown("说明\n\n```python\nprint(1)\n```\n")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0], MarkdownBlock(("说明",)))
        self.assertEqual(blocks[1], CodeBlock("python", ("print(1)",)))

    def test_headings_start_new_blocks(self):
        blocks = parse_markdown("# 标题\n\n段落\n\n## 小节\n\n内容\n")
        self.assertEqual(
            blocks,
            [
                MarkdownBlock(("# 标题", "", "段落")),
                MarkdownBlock(("## 小节", "", "内容")),
            ],
        )

    def test_non_python_language_kept(self):
        blocks = parse_markdown("```bash\necho hi\n```\n")
        self.assertEqual(blocks, [CodeBlock("bash", ("echo hi",))])

    def test_empty_language_fence(self):
        blocks = parse_markdown("```\nraw\n```\n")
        self.assertEqual(blocks, [CodeBlock("", ("raw",))])

    def test_comment_inside_fence_is_not_heading(self):
        blocks = parse_markdown("```python\n# 注释\nx = 1\n```\n")
        self.assertEqual(blocks, [CodeBlock("python", ("# 注释", "x = 1"))])

    def test_blank_lines_inside_fence_trimmed(self):
        blocks = parse_markdown("```python\n\nprint(1)\n\n```\n")
        self.assertEqual(blocks, [CodeBlock("python", ("print(1)",))])

    def test_blank_lines_inside_prose_kept(self):
        blocks = parse_markdown("第一段\n\n第二段\n")
        self.assertEqual(blocks, [MarkdownBlock(("第一段", "", "第二段"))])

    def test_crlf_input(self):
        blocks = parse_markdown("说明\r\n\r\n```python\r\nx = 1\r\n```\r\n")
        self.assertEqual(blocks[1], CodeBlock("python", ("x = 1",)))

    def test_unclosed_fence_raises_with_line_number(self):
        with self.assertRaises(MarkdownParseError) as caught:
            parse_markdown("说明\n\n```python\nx = 1\n")
        self.assertIn("第 3 行", str(caught.exception))

    def test_empty_text(self):
        self.assertEqual(parse_markdown(""), [])
        self.assertEqual(parse_markdown("\n\n"), [])


if __name__ == "__main__":
    unittest.main()
