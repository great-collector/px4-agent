from pathlib import Path
def directory_tree(directory: str ="./", max_depth: int = 10, max_entries: int = 100000) -> str:
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


project_root = resolve_project_root()

with open("tree.txt", "w", encoding="utf-8") as f:
    f.write(directory_tree(project_root))