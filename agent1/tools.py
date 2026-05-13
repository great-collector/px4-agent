from langchain_core.tools import tool
from pathlib import Path
import os

def resolve_project_root() -> Path:
    env_root = os.getenv("PX4_MODULES_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parent.parent.parent / "PX4-Autopilot" / "src" / "modules"


@tool
def read_file_as_comment(
    file_path: str | Path,
    *,
    encoding: str = "utf-8",
    max_chars: int = 50_000,) -> str:
    """
    根据路径读取文件内容，返回可直接用于提示词/日志的 comment 字符串。

    - 文件不存在/不是文件：返回包含错误信息的 comment
    - 解码失败：自动回退为 utf-8(errors="replace")
    - 内容过长：按 max_chars 截断
    """
    p = Path(file_path).expanduser().resolve()
    if not p.exists():
        return f"[FileNotFoundError] 文件不存在: {p}"
    if not p.is_file():
        return f"[NotAFile] 不是文件: {p}"

    try:
        content = p.read_text(encoding=encoding)
    except UnicodeDecodeError:
        content = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[ReadError] 读取失败: {p} ({type(e).__name__}: {e})"

    if max_chars is not None and max_chars > 0 and len(content) > max_chars:
        content = content[:max_chars] + "\n...[truncated]"

    return content

from pathlib import Path
from langchain.tools import tool


@tool
def directory_tree(directory: str ="./", max_depth: int = 3, max_entries: int = 100000) -> str:
    """
    输入一个目录路径，返回该目录的树状结构，功能类似 tree 命令。

    Args:
        directory: 要查看的目录路径。默认"./"
        max_depth: 最大递归深度，默认 3。
        max_entries: 最多显示的文件/目录数量，默认 100000

    Returns:
        目录的树状结构字符串。
    """
    root = Path(directory).expanduser().resolve()

    if not root.exists():
        return f"路径不存在：{root}"

    if not root.is_dir():
        return f"这不是一个目录：{root}"

    lines = [f"{root.name}/"]
    count = 0

    def build_tree(path: Path, prefix: str = "", depth: int = 0):
        nonlocal count

        if depth >= max_depth:
            return

        if count >= max_entries:
            return

        try:
            children = sorted(
                path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            lines.append(prefix + "└── [权限不足]")
            return
        except Exception as e:
            lines.append(prefix + f"└── [读取失败: {e}]")
            return

        for index, child in enumerate(children):
            if count >= max_entries:
                lines.append(prefix + "└── ... [输出已截断]")
                return

            is_last = index == len(children) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if child.is_dir() else ""

            lines.append(prefix + connector + child.name + suffix)
            count += 1

            if child.is_dir():
                extension = "    " if is_last else "│   "
                build_tree(child, prefix + extension, depth + 1)

    build_tree(root)

    return "\n".join(lines)

@tool
def get_modules_tree() -> str:
    """
    这个函数返回PX4的modules目录的树状结构,这个目录结构是提前写死的

    Args: None

    Returns:
        目录的树状结构字符串。
    """
    tree=""
    with open("src/module_tree.txt", "r", encoding="utf-8") as f:
        tree=f.read()
    return tree

from pathlib import Path
from langchain.tools import tool


@tool
def write_text_file(file_path: str ="output/agent1_report.md", content: str ="", encoding: str = "utf-8") -> str:
    """
    将指定内容写入到指定文件中。

    Args:
        file_path: 要写入的文件路径,默认report.md
        content: 要写入的文本内容。
        encoding: 文件编码，默认 utf-8。

    Returns:
        写入成功或失败的信息。
    """
    try:
        path = Path(file_path).expanduser().resolve()

        # 如果父目录不存在，自动创建
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding=encoding) as f:
            f.write(content)

        return f"写入成功：{path}"

    except Exception as e:
        return f"写入失败：{type(e).__name__}: {e}"