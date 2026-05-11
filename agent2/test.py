import os
from langchain.agents import create_agent
from dotenv import load_dotenv
from tools import *
from langchain_deepseek import ChatDeepSeek

import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logging.info("程序开始运行")
logging.warning("这是一个警告")
logging.error("这里发生了错误")




load_dotenv(override=True)
project_root=r"E:\个人文件\比赛\26人智\PX4\PX4-Autopilot\src\modules"

def create_agent2(llm):
   
    return create_agent(
        model=llm,
        tools=[read_file_as_comment,directory_tree,get_modules_tree,write_text_file,run_cppcheck_json],
        system_prompt=(
            "现在是测试环境\n"
            "你的任务是测试工具run_cppcheck_json是否能够正常工作\n"
            "还有一些其他工具,你可以使用get_modules_tree函数获取PX4的模块树,read_file_as_comment函数读取模块文件的内容,directory_tree函数读取模块目录的树状结构"
        ),
        name="agent2",
    )

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
)
agent1=create_agent2(llm)

result1 = agent1.invoke({
            "messages": [{"role": "user", "content": f"""
                          你用一下run_cppcheck_json工具,随便检测一个模块目录
                          """}]
        })

logging.info(result1)
print(result1["messages"][-1].content)