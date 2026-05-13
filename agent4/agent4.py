import os
from langchain.agents import create_agent
from dotenv import load_dotenv
from pathlib import Path
from tools import *
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)
project_root = resolve_project_root()

report_template=read_file_as_comment("src/report_template.md")
def create_agent4(llm):
   
    return create_agent(
        model=llm,
        tools=[append_text_file],
        system_prompt=(
            "你是PX4安全检测系统的动态仿真检测模块的agent4\n"
            f"你的职责是根据agent1,agent2,agent3的漏洞检测报告,总结完整的漏洞检测报告,可参考的报告模板{report_template}\n"
            "你可以使用append_text_file函数分段追加写入文件中,这样可以防止结果过长,无法写入\n"
            "所有输出路径应该在 output/ 文件夹下\n"
        ),
        name="agent4",
    )

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
)
agent4=create_agent4(llm)

if __name__ == "__main__":
    current_file_dir = Path(__file__).parent.resolve()

    agent1_report_path = current_file_dir.parent /"agent1" /"report.md"
    agent1_report = read_file_as_comment(agent1_report_path)

    agent2_report_path = current_file_dir.parent /"agent2" /"report.md"
    agent2_report = read_file_as_comment(agent2_report_path)

    agent3_report_path = current_file_dir.parent /"agent3" /"report3.md"
    agent3_report = read_file_as_comment(agent3_report_path)



    result4 = agent4.invoke({
                "messages": [{"role": "user", "content": f"""
                            根据这三份报告:{agent1_report},{agent2_report},{agent3_report},总结完整的漏洞检测报告,
                            注意输出完整的漏洞内容,不要遗漏任何漏洞,疑似漏洞的部分也要输出
                            注意当前是2026年
                            """}]
            })

    print(result4)
    print(result4["messages"][-1].content)