
from pathlib import Path
from tools import *
# from agent1.tools import *
from agent1.agent1 import agent1
# from agent2.tools import *
from agent2.agent2 import agent2
# from agent3.tools import *
from agent3.agent3 import agent3
# from agent4.tools import *
from agent4.agent4 import agent4
import logging

LOG_DIR = Path(__file__).parent.resolve() / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logging.info("程序启动")

#-------------------------------------------------------------------------
print("初始化")
project_root=r"E:\个人文件\比赛\26人智\PX4\PX4-Autopilot\src\modules"

version=get_base_info(project_root)
sum_of_modules=count_directories(project_root)

with open("src/base_imfo.txt", "w", encoding="utf-8") as f:
    f.write(f"软件版本:{version}\n")
    f.write(f"模块总数:{sum_of_modules}")

tree=directory_tree(project_root)
with open("src/module_tree.txt", "w", encoding="utf-8") as f:
    f.write(tree)
    
#-------------------------------------------------------------------------
print("agent1执行")
result1 = agent1.invoke({
                "messages": [{"role": "user", "content": f"""
                            以你的知识,看看这个版本的px模块可能哪里出现漏洞,输出一份报告,报告格式为markdown,报告内容包括漏洞的文件路径,漏洞的描述,漏洞的严重程度
                            输出报告路径:"output/report1.md"
                            """}]
            })
logging.info(result1)
logging.info("agent1执行完成")
#-------------------------------------------------------------------------
print("agent2执行")
result2 = agent2.invoke({
            "messages": [{"role": "user", "content": f"""
                          以你的能力,看看这个版本的px模块可能哪里出现漏洞,输出一份报告,报告格式为markdown,报告内容包括漏洞的文件路径,漏洞的描述,漏洞的严重程度
                          输出报告路径:"output/report2.md"
                          """}]
        })
logging.info(result2)
logging.info("agent2执行完成")
#-------------------------------------------------------------------------
print("agent3执行")
agent1_report_path ="output/report1.md"
agent1_report = read_file_as_comment(agent1_report_path)

agent2_report_path ="output/report2.md"
agent2_report = read_file_as_comment(agent2_report_path)

result3 = agent3.invoke({
            "messages": [{"role": "user", "content": f"""
                        根据这两份报告:{agent1_report},{agent2_report},进行仿真测试,并撰写仿真测试结果
                        输出报告路径:"output/report3.md"
                        """}]
        })
logging.info(result3)
logging.info("agent3执行完成")
#-------------------------------------------------------------------------
print("agent4执行")
agent3_report_path ="output/report3.md"
agent3_report = read_file_as_comment(agent3_report_path)

result4 = agent4.invoke({
            "messages": [{"role": "user", "content": f"""
                          根据这三份报告:{agent1_report},{agent2_report},{agent3_report},总结并生成完整的漏洞检测报告,
                          注意当前是2026年
                          输出报告路径:"output/report4.md"
                          """}]
        })
logging.info(result4)
logging.info("agent4执行完成")
#-------------------------------------------------------------------------
print("程序结束")