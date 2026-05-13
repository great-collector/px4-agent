import os
from pathlib import Path
from langchain.agents import create_agent
from dotenv import load_dotenv
from tools import *
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)
project_root = resolve_project_root()


def create_agent3(llm):
   
    return create_agent(
        model=llm,
        tools=[detect_test,write_text_file],
        system_prompt=(
            "当前是测试环境\n"
            "你是PX4安全检测系统的动态仿真检测模块的agent3,仿真检测工具detect_test\n"
            "你的职责是根据agent1和agent2的漏洞检测报告,仿真检测漏洞的真实性\n"
            "你可以使用write_text_file函数将结果写入文件中\n"
            "所有输出路径应该在 output/ 文件夹下\n"
        ),
        name="agent3",
    )

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
)
agent3=create_agent3(llm)

if __name__ == "__main__":
    current_file_dir = Path(__file__).parent.resolve()

    agent1_report_path = current_file_dir.parent /"agent1" /"report.md"
    agent1_report = read_file_as_comment(agent1_report_path)

    agent2_report_path = current_file_dir.parent /"agent2" /"report.md"
    agent2_report = read_file_as_comment(agent2_report_path)





    result3 = agent3.invoke({
                "messages": [{"role": "user", "content": f"""
                            根据这两份报告:{agent1_report},{agent2_report},进行仿真测试,并撰写仿真测试结果
                            """}]
            })

    print(result3)
    print(result3["messages"][-1].content)