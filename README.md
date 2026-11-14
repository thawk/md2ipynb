# md2ipynb

把课程 Markdown 转成 Jupyter Notebook。

- 正文（标题、段落、表格、列表、引用）→ markdown 单元格
- `python` / `py` / `python3` 代码块 → code 单元格
- 其他代码块（`bash`、`powershell`、`text`、`json`、`yaml`、`mermaid`、`markdown`、`python-reference` 等）→ markdown 单元格中的围栏代码块，保留原语言标记
- 单元格带唯一 id，输出为空，元数据与课程 Notebook 一致（`.venv-client` 内核）

## 快速开始（uv）

```bash
cd tools/md2ipynb
uv sync
uv run md2ipynb ../../01-model-api.md
```

`uv run` 会把本包以可编辑模式装进项目内的 `.venv`，之后直接用入口命令即可：

```bash
uv run md2ipynb ../../01-model-api.md ../../02-vllm-deployment.md
uv run md2ipynb -o ../../notebooks ../../01-model-api.md
uv run md2ipynb -f ../../01-model-api.md
```

`uv sync` 会同时安装默认 dev 依赖（pytest），所以测试也能直接跑：

```bash
uv run pytest
```

## 用 Makefile

```bash
make sync
make run FILES="../../01-model-api.md ../../02-vllm-deployment.md"
make run FILES="../../01-model-api.md" OUTPUT_DIR="../../notebooks" FORCE=1
make test
```

| 目标 | 说明 |
| --- | --- |
| `make sync` | `uv sync`，创建/更新 `.venv` 并安装依赖 |
| `make run FILES=...` | `uv run md2ipynb`，必须给 `FILES` |
| `make test` | `uv run pytest` |
| `make test-stdlib` | 只用标准库：`PYTHONPATH=src uv run python -m unittest discover -s tests` |
| `make clean` | 删除 `.venv`、缓存与构建产物 |
| `make help` | 显示可用目标（默认目标） |

可覆盖的变量：`FILES`、`OUTPUT_DIR`、`FORCE`（非空即覆盖）、`UV`（默认 `uv`，可指向其他二进制路径）。

## 命令行参数

```bash
md2ipynb [选项] MD [MD ...]
```

| 参数 | 说明 |
| --- | --- |
| `MD ...` | 一个或多个待转换的 Markdown 文件 |
| `-o, --output-dir` | 输出目录，默认与源文件同目录；不存在时自动创建 |
| `-f, --force` | 覆盖已存在的 `.ipynb`，默认跳过并提示 |
| `-q, --quiet` | 不打印成功信息 |
| `-V, --version` | 显示版本 |

退出码：全部成功（含跳过）为 0；文件读取失败、围栏未闭合等错误为 1。

## 不使用 uv

用当前 Python 安装：

```bash
python -m pip install -e .
md2ipynb ../../01-model-api.md
```

不安装、直接运行：

```bash
PYTHONPATH=src python -m md2ipynb ../../01-model-api.md
PYTHONPATH=src python -m unittest discover -s tests   # 测试也只用标准库
```

## 作为库调用

```python
from md2ipynb import convert_file, convert_text

notebook = convert_text("# 标题\n\n```python\nprint('hello')\n```\n")

result = convert_file("01-model-api.md", output_dir="notebooks", overwrite=True)
print(result.output, result.markdown_cells, result.code_cells)
```

## 测试

```bash
uv run pytest                 # 或 make test
make test-stdlib              # 不依赖 pytest
```

## 目录结构

```
md2ipynb/
├── pyproject.toml
├── Makefile
├── README.md
├── src/md2ipynb/
│   ├── __init__.py     导出 API
│   ├── __main__.py     python -m md2ipynb
│   ├── blocks.py       块类型定义
│   ├── parser.py       Markdown → 块序列
│   ├── notebook.py     块序列 → Notebook JSON
│   ├── converter.py    文件读取、写出与覆盖策略
│   └── cli.py          命令行入口
└── tests/
```
