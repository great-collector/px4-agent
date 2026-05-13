from tools import *
from pathlib import Path

project_root = resolve_project_root()

version=get_base_info(project_root)
sum_of_modules=count_directories(project_root)

with open("base_imfo.txt", "w", encoding="utf-8") as f:
    f.write(f"软件版本:{version}\n")
    f.write(f"模块总数:{sum_of_modules}")

tree=directory_tree(project_root)
with open("module_tree.txt", "w", encoding="utf-8") as f:
    f.write(tree)
    