"""把 Markdown 文本切分为正文块与围栏代码块。"""

from __future__ import annotations

import re

from .blocks import Block, CodeBlock, MarkdownBlock

_OPEN_FENCE = re.compile(r"^```([^\s`]*)\s*$")
_CLOSE_FENCE = re.compile(r"^\s*```\s*$")
_HEADING = re.compile(r"^#{1,6}\s")


class MarkdownParseError(ValueError):
    """Markdown 结构不完整，例如代码围栏没有闭合。"""


def trim_blank(lines: list[str]) -> list[str]:
    """去掉首尾空行，保留中间的空行。"""
    start, end = 0, len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def parse_markdown(text: str) -> list[Block]:
    """按标题与代码围栏切分文本。

    标题会开启新的正文块，避免多个小节挤在同一个单元格里；
    正文内部的空行、列表和表格保持原样。
    """
    blocks: list[Block] = []
    current: list[str] = []
    fence_language: str | None = None
    fence_start = 0
    code_lines: list[str] = []

    def flush_markdown() -> None:
        lines = trim_blank(current)
        if lines:
            blocks.append(MarkdownBlock(tuple(lines)))
        current.clear()

    for number, line in enumerate(text.splitlines(), start=1):
        if fence_language is None:
            opening = _OPEN_FENCE.match(line)
            if opening:
                flush_markdown()
                fence_language = (opening.group(1) or "").lower()
                fence_start = number
                code_lines = []
                continue
            if _HEADING.match(line):
                flush_markdown()
            current.append(line)
            continue

        if _CLOSE_FENCE.match(line):
            blocks.append(
                CodeBlock(fence_language, tuple(trim_blank(code_lines)))
            )
            fence_language = None
            continue
        code_lines.append(line)

    if fence_language is not None:
        raise MarkdownParseError(f"第 {fence_start} 行的代码围栏没有闭合")

    flush_markdown()
    return blocks
