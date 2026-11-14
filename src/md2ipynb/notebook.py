"""把块序列组装成 nbformat 4.5 的 Notebook 字典。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Iterable, Optional, Sequence
from uuid import uuid4

from .blocks import Block, CodeBlock, MarkdownBlock, PYTHON_LANGUAGES

DEFAULT_METADATA: dict[str, Any] = {
    "kernelspec": {
        "display_name": ".venv-client",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.12.16",
    },
}

IdFactory = Callable[[], str]


def new_cell_id() -> str:
    return uuid4().hex[:8]


def build_notebook(
    blocks: Iterable[Block],
    *,
    metadata: Optional[dict[str, Any]] = None,
    id_factory: Optional[IdFactory] = None,
) -> dict[str, Any]:
    """把块序列转成 Notebook；不落盘。"""
    make_id = id_factory or new_cell_id
    cells = [_build_cell(block, make_id) for block in blocks]
    return {
        "cells": cells,
        "metadata": deepcopy(DEFAULT_METADATA if metadata is None else metadata),
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def _build_cell(block: Block, make_id: IdFactory) -> dict[str, Any]:
    if isinstance(block, CodeBlock) and block.language in PYTHON_LANGUAGES:
        return {
            "cell_type": "code",
            "execution_count": None,
            "id": make_id(),
            "metadata": {},
            "outputs": [],
            "source": to_source(block.lines),
        }
    if isinstance(block, CodeBlock):
        return {
            "cell_type": "markdown",
            "id": make_id(),
            "metadata": {},
            "source": to_source(render_fence(block)),
        }
    assert isinstance(block, MarkdownBlock)
    return {
        "cell_type": "markdown",
        "id": make_id(),
        "metadata": {},
        "source": to_source(block.lines),
    }


def render_fence(block: CodeBlock) -> list[str]:
    """把非 Python 代码块还原为 markdown 围栏。"""
    lines = ["```" + block.language]
    lines.extend(block.lines)
    lines.append("```")
    return lines


def to_source(lines: Sequence[str]) -> list[str]:
    """按 nbformat 约定把行转成 source 列表：除最后一行外都带换行。"""
    if not lines:
        return []
    return [line + "\n" for line in lines[:-1]] + [lines[-1]]
