"""读取 Markdown、生成并写出 Notebook。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .notebook import IdFactory, build_notebook
from .parser import parse_markdown


class OutputExistsError(FileExistsError):
    """目标 Notebook 已存在且未允许覆盖。"""

    def __init__(self, path: Path):
        super().__init__(f"{path} 已存在；使用 -f/--force 覆盖")
        self.path = Path(path)


@dataclass(frozen=True)
class ConversionResult:
    source: Path
    output: Path
    markdown_cells: int
    code_cells: int

    @property
    def total_cells(self) -> int:
        return self.markdown_cells + self.code_cells


def convert_text(
    text: str,
    *,
    metadata: Optional[dict[str, Any]] = None,
    id_factory: Optional[IdFactory] = None,
) -> dict[str, Any]:
    """把 Markdown 文本转成 Notebook 字典。"""
    return build_notebook(
        parse_markdown(text), metadata=metadata, id_factory=id_factory
    )


def convert_file(
    source: Path | str,
    *,
    output: Optional[Path | str] = None,
    output_dir: Optional[Path | str] = None,
    overwrite: bool = False,
    metadata: Optional[dict[str, Any]] = None,
    id_factory: Optional[IdFactory] = None,
) -> ConversionResult:
    """把单个 Markdown 文件写成同名 Notebook。

    output 与 output_dir 只能给一个：前者是完整目标路径，后者是输出目录。
    """
    if output is not None and output_dir is not None:
        raise ValueError("output 与 output_dir 只能指定一个")

    source_path = Path(source)
    output_path = _resolve_output(source_path, output, output_dir)
    if output_path.exists() and not overwrite:
        raise OutputExistsError(output_path)

    notebook = convert_text(
        source_path.read_text(encoding="utf-8"),
        metadata=metadata,
        id_factory=id_factory,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_notebook(notebook, output_path)

    code_cells = sum(1 for cell in notebook["cells"] if cell["cell_type"] == "code")
    return ConversionResult(
        source=source_path,
        output=output_path,
        markdown_cells=len(notebook["cells"]) - code_cells,
        code_cells=code_cells,
    )


def write_notebook(notebook: dict[str, Any], path: Path | str) -> Path:
    target = Path(path)
    target.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    return target


def _resolve_output(
    source: Path,
    output: Optional[Path | str],
    output_dir: Optional[Path | str],
) -> Path:
    if output is not None:
        return Path(output)
    name = source.with_suffix(".ipynb").name
    if output_dir is not None:
        return Path(output_dir) / name
    return source.with_suffix(".ipynb")
