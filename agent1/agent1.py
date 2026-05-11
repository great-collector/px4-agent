import os
from langchain.agents import create_agent
from dotenv import load_dotenv
from tools import *
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)
project_root=r"E:\个人文件\比赛\26人智\PX4\PX4-Autopilot\src\modules"
vulnerabilities=""
with open("src/vulnerabilities.txt", "r", encoding="utf-8") as f:
    vulnerabilities=f.read()

def create_agent1(llm):
   
    return create_agent(
        model=llm,
        tools=[read_file_as_comment,directory_tree,get_modules_tree,write_text_file],
        system_prompt=(
            "你是PX4安全检测系统的一个基于软件供应链的安全缺陷检测模块的agent1,\n"
            "你的职责是根据现有的漏洞知识,检测PX4的模块可能出现漏洞的地方\n"
            "你不需要对代码具体分析,只需要找到与漏洞知识库相匹配的漏洞即可\n"
            f"你有以下漏洞知识:{vulnerabilities}\n"
            "你可以使用get_modules_tree函数获取PX4的模块树,read_file_as_comment函数读取模块文件的内容,directory_tree函数读取模块目录的树状结构,write_text_file函数将结果写入文件中\n"            
        ),
        name="agent1",
    )

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
)
agent1=create_agent1(llm)

if __name__ == "__main__":

    result1 = agent1.invoke({
                "messages": [{"role": "user", "content": f"""
                            以你的知识,看看这个版本的px模块可能哪里出现漏洞,输出一份报告,报告格式为markdown,报告内容包括漏洞的文件路径,漏洞的描述,漏洞的严重程度
                            """}]
            })

    print(result1)
    print(result1["messages"][-1].content)