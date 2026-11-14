"""解析后的 Markdown 块。

解析器只负责把文本切成块；块如何变成 Notebook 单元格由 notebook 模块决定。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

#: 视作可执行 Python 的围栏语言标记
PYTHON_LANGUAGES = frozenset({"python", "py", "python3"})


@dataclass(frozen=True)
class MarkdownBlock:
    """普通正文，多个段落或表格可能在同一块中。"""

    lines: tuple[str, ...]


@dataclass(frozen=True)
class CodeBlock:
    """围栏代码块；language 为空字符串表示无语言标记。"""

    language: str
    lines: tuple[str, ...]


Block = Union[MarkdownBlock, CodeBlock]
