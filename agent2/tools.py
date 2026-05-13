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
def write_text_file(file_path: str ="output/agent2_report.md", content: str ="", encoding: str = "utf-8") -> str:
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
    
    
from langchain.tools import tool
from pathlib import Path
import subprocess
import csv
import json


def safe_str(value) -> str:
    """
    防止 None.strip() 报错。
    """
    if value is None:
        return ""
    return str(value)


@tool
def run_flawfinder(project_dir: str) -> str:
    """
    使用 Flawfinder 扫描 C/C++ 源码中的潜在安全缺陷。

    输入：
        project_dir: 需要扫描的项目目录

    输出：
        JSON 字符串，包括扫描状态、问题数量、高危问题、报告路径
    """

    project_path = Path(project_dir)

    if not project_path.exists():
        return json.dumps({
            "tool": "flawfinder",
            "success": False,
            "error": f"目录不存在：{project_dir}"
        }, ensure_ascii=False, indent=2)

    if not project_path.is_dir():
        return json.dumps({
            "tool": "flawfinder",
            "success": False,
            "error": f"输入路径不是目录：{project_dir}"
        }, ensure_ascii=False, indent=2)

    report_dir = project_path / "security_reports"
    report_dir.mkdir(exist_ok=True)

    csv_report = report_dir / "flawfinder_report.csv"

    cmd = [
        "flawfinder",
        "--csv",
        "--quiet",
        str(project_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=300
        )

        csv_content = result.stdout or ""

        if not csv_content.strip():
            return json.dumps({
                "tool": "flawfinder",
                "success": False,
                "error": "Flawfinder 没有产生有效 CSV 输出",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }, ensure_ascii=False, indent=2)

        with open(csv_report, "w", encoding="utf-8", newline="") as f:
            f.write(csv_content)

        findings = []

        with open(csv_report, "r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if not row:
                    continue

                level = safe_str(row.get("Level")).strip()

                finding = {
                    "file": safe_str(row.get("File")).strip(),
                    "line": safe_str(row.get("Line")).strip(),
                    "column": safe_str(row.get("Column")).strip(),
                    "level": level,
                    "category": safe_str(row.get("Category")).strip(),
                    "function": safe_str(row.get("Name")).strip(),
                    "warning": safe_str(row.get("Warning")).strip(),
                    "suggestion": safe_str(row.get("Suggestion")).strip(),
                    "note": safe_str(row.get("Note")).strip(),
                    "cwe": safe_str(row.get("CWE")).strip()
                }

                # 避免把完全空行计入结果
                if any(finding.values()):
                    findings.append(finding)

        high_risk_findings = []

        for item in findings:
            level = item.get("level", "")

            if level.isdigit() and int(level) >= 4:
                high_risk_findings.append(item)

        output = {
            "tool": "flawfinder",
            "success": True,
            "project_dir": str(project_path),
            "report_path": str(csv_report),
            "summary": {
                "total_findings": len(findings),
                "high_risk_findings": len(high_risk_findings)
            },
            "high_risk_examples": high_risk_findings[:10],
            "all_findings": findings[:100]
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except FileNotFoundError:
        return json.dumps({
            "tool": "flawfinder",
            "success": False,
            "error": "未找到 flawfinder 命令，请先执行：pip install flawfinder"
        }, ensure_ascii=False, indent=2)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "tool": "flawfinder",
            "success": False,
            "error": "Flawfinder 扫描超时"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "tool": "flawfinder",
            "success": False,
            "error": str(e)
        }, ensure_ascii=False, indent=2)



@tool
def run_semgrep_json(project_dir: str) -> str:
    """
    使用 Semgrep 对项目进行静态安全扫描，并返回 JSON 格式结果。

    输入：
        project_dir: 需要扫描的项目目录

    输出：
        JSON 字符串，包括扫描状态、问题数量、高危问题、报告路径
    """

    project_path = Path(project_dir)

    if not project_path.exists():
        return json.dumps({
            "tool": "semgrep",
            "success": False,
            "error": f"目录不存在：{project_dir}"
        }, ensure_ascii=False, indent=2)

    if not project_path.is_dir():
        return json.dumps({
            "tool": "semgrep",
            "success": False,
            "error": f"输入路径不是目录：{project_dir}"
        }, ensure_ascii=False, indent=2)

    report_dir = project_path / "security_reports"
    report_dir.mkdir(exist_ok=True)

    report_file = report_dir / "semgrep_report.json"

    cmd = [
        "semgrep",
        "scan",
        "--config", "p/security-audit",
        "--json",
        "-o", str(report_file),
        str(project_path)
    ]

    env = os.environ.copy()

    # 关键：强制 Python / Semgrep 使用 UTF-8，避免 Windows GBK 编码崩溃
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["LC_ALL"] = "C.UTF-8"
    env["LANG"] = "C.UTF-8"

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=600
        )

        if not report_file.exists():
            return json.dumps({
                "tool": "semgrep",
                "success": False,
                "error": "Semgrep 未生成报告文件",
                "returncode": result.returncode,
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-4000:]
            }, ensure_ascii=False, indent=2)

        with open(report_file, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        raw_results = data.get("results", [])

        findings = []

        for item in raw_results:
            extra = item.get("extra", {})

            finding = {
                "file": item.get("path", ""),
                "line": item.get("start", {}).get("line", ""),
                "column": item.get("start", {}).get("col", ""),
                "end_line": item.get("end", {}).get("line", ""),
                "rule_id": item.get("check_id", ""),
                "message": extra.get("message", ""),
                "severity": extra.get("severity", ""),
                "metadata": extra.get("metadata", {})
            }

            findings.append(finding)

        high_risk_findings = [
            item for item in findings
            if str(item.get("severity", "")).upper() in ["ERROR", "HIGH", "CRITICAL"]
        ]

        output = {
            "tool": "semgrep",
            "success": True,
            "project_dir": str(project_path),
            "report_path": str(report_file),
            "summary": {
                "total_findings": len(findings),
                "high_risk_findings": len(high_risk_findings)
            },
            "high_risk_examples": high_risk_findings[:10],
            "all_findings": findings[:100]
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except FileNotFoundError:
        return json.dumps({
            "tool": "semgrep",
            "success": False,
            "error": "未找到 semgrep 命令，请先执行：pip install semgrep"
        }, ensure_ascii=False, indent=2)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "tool": "semgrep",
            "success": False,
            "error": "Semgrep 扫描超时"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "tool": "semgrep",
            "success": False,
            "error": str(e)
        }, ensure_ascii=False, indent=2)
        
        
from langchain.tools import tool
from pathlib import Path
import subprocess
import json
import xml.etree.ElementTree as ET


@tool
def run_cppcheck_json(project_dir: str) -> str: #这个工具有点问题,先别用
    """
    使用 Cppcheck 扫描 C/C++ 源码中的潜在缺陷，并返回 JSON 格式结果。

    输入：
        project_dir: 需要扫描的项目目录

    输出：
        JSON 字符串，包括扫描状态、问题数量、高危问题、报告路径
    """

    project_path = Path(project_dir)

    if not project_path.exists():
        return json.dumps({
            "tool": "cppcheck",
            "success": False,
            "error": f"目录不存在：{project_dir}"
        }, ensure_ascii=False, indent=2)

    if not project_path.is_dir():
        return json.dumps({
            "tool": "cppcheck",
            "success": False,
            "error": f"输入路径不是目录：{project_dir}"
        }, ensure_ascii=False, indent=2)

    report_dir = project_path / "security_reports"
    report_dir.mkdir(exist_ok=True)

    xml_report = report_dir / "cppcheck_report.xml"

    cmd = [
        "cppcheck",
        "--enable=all",
        "--inconclusive",
        "--xml",
        "--xml-version=2",
        "--suppress=missingIncludeSystem",
        str(project_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=900
        )

        # Cppcheck 的 XML 报告一般输出到 stderr
        xml_content = result.stderr

        if not xml_content.strip():
            return json.dumps({
                "tool": "cppcheck",
                "success": True,
                "message": "Cppcheck 扫描完成，但未产生有效 XML 输出",
                "stdout": result.stdout
            }, ensure_ascii=False, indent=2)

        with open(xml_report, "w", encoding="utf-8") as f:
            f.write(xml_content)

        findings = []

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            return json.dumps({
                "tool": "cppcheck",
                "success": False,
                "error": "Cppcheck XML 解析失败",
                "detail": str(e),
                "report_path": str(xml_report)
            }, ensure_ascii=False, indent=2)

        errors_node = root.find("errors")

        if errors_node is not None:
            for error in errors_node.findall("error"):
                severity = error.attrib.get("severity", "")
                msg = error.attrib.get("msg", "")
                verbose = error.attrib.get("verbose", "")
                error_id = error.attrib.get("id", "")
                cwe = error.attrib.get("cwe", "")

                locations = error.findall("location")

                if locations:
                    for loc in locations:
                        finding = {
                            "file": loc.attrib.get("file", ""),
                            "line": loc.attrib.get("line", ""),
                            "column": loc.attrib.get("column", ""),
                            "severity": severity,
                            "id": error_id,
                            "message": msg,
                            "verbose": verbose,
                            "cwe": cwe
                        }
                        findings.append(finding)
                else:
                    finding = {
                        "file": "",
                        "line": "",
                        "column": "",
                        "severity": severity,
                        "id": error_id,
                        "message": msg,
                        "verbose": verbose,
                        "cwe": cwe
                    }
                    findings.append(finding)

        high_risk_findings = [
            item for item in findings
            if str(item.get("severity", "")).lower() in [
                "error",
                "warning"
            ]
        ]

        output = {
            "tool": "cppcheck",
            "success": True,
            "project_dir": str(project_path),
            "report_path": str(xml_report),
            "summary": {
                "total_findings": len(findings),
                "high_risk_findings": len(high_risk_findings)
            },
            "high_risk_examples": high_risk_findings[:10],
            "all_findings": findings
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except FileNotFoundError:
        return json.dumps({
            "tool": "cppcheck",
            "success": False,
            "error": "未找到 cppcheck 命令，请先安装 cppcheck，例如：conda install -c conda-forge cppcheck"
        }, ensure_ascii=False, indent=2)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "tool": "cppcheck",
            "success": False,
            "error": "Cppcheck 扫描超时"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "tool": "cppcheck",
            "success": False,
            "error": str(e)
        }, ensure_ascii=False, indent=2)