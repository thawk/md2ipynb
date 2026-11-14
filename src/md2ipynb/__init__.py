"""md2ipynb：把课程 Markdown 转成 Jupyter Notebook。"""

from __future__ import annotations

from .converter import (
    ConversionResult,
    OutputExistsError,
    convert_file,
    convert_text,
    write_notebook,
)
from .notebook import DEFAULT_METADATA, build_notebook
from .parser import MarkdownParseError, parse_markdown

__version__ = "0.1.0"

__all__ = [
    "ConversionResult",
    "DEFAULT_METADATA",
    "MarkdownParseError",
    "OutputExistsError",
    "__version__",
    "build_notebook",
    "convert_file",
    "convert_text",
    "parse_markdown",
    "write_notebook",
]
