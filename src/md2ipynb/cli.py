"""命令行入口：把命令行给出的 Markdown 文件转换成 Notebook。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from . import __version__
from .converter import OutputExistsError, convert_file
from .parser import MarkdownParseError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2ipynb",
        description="把 Markdown 转成 ipynb：正文进 markdown 单元格，python 代码块进 code 单元格。",
    )
    parser.add_argument(
        "sources",
        nargs="+",
        metavar="MD",
        type=Path,
        help="待转换的 Markdown 文件，可一次给多个",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="输出目录；默认写到源文件同目录",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="覆盖已存在的 .ipynb；默认跳过",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="不打印成功信息",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    status = 0
    for source in args.sources:
        try:
            result = convert_file(
                source,
                output_dir=args.output_dir,
                overwrite=args.force,
            )
        except OutputExistsError as error:
            if not args.quiet:
                print(f"跳过：{error.path} 已存在（加 -f 覆盖）", file=sys.stderr)
        except (OSError, MarkdownParseError) as error:
            print(f"错误：{source}：{error}", file=sys.stderr)
            status = 1
        else:
            if not args.quiet:
                print(
                    f"{result.source.name} -> {result.output}"
                    f"（markdown {result.markdown_cells}，code {result.code_cells}）"
                )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
