import os
from langchain.agents import create_agent
from dotenv import load_dotenv
from tools import *
from langchain_deepseek import ChatDeepSeek



load_dotenv(override=True)
project_root=r"E:\个人文件\比赛\26人智\PX4\PX4-Autopilot\src\modules"

def create_agent2(llm):
   
    return create_agent(
        model=llm,
        tools=[read_file_as_comment,directory_tree,get_modules_tree,write_text_file,run_flawfinder,run_semgrep_json],
        system_prompt=(
            "你是PX4安全检测系统的一个代码安全缺陷静态检测agent2,\n"
            "你的任务是对具体的代码进行安全缺陷静态检测\n"
            "你拥有一些静态检测工具,如run_flawfinder,run_semgrep_json,你可以使用这些工具检测PX4的代码安全缺陷,当然也要有自己的判断\n"
            "还有一些其他工具,你可以使用get_modules_tree函数获取PX4的模块树,read_file_as_comment函数读取模块文件的内容,directory_tree函数读取模块目录的树状结构,write_text_file函数将结果写入报告中\n"            
        ),
        name="agent2",
    )

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
)
agent2=create_agent2(llm)


if __name__ == "__main__":
    result1 = agent2.invoke({
            "messages": [{"role": "user", "content": f"""
                          以你的能力,看看这个版本的px模块可能哪里出现漏洞,输出一份报告,报告格式为markdown,报告内容包括漏洞的文件路径,漏洞的描述,漏洞的严重程度
                          """}]
        })

    print(result1["messages"][-1].content)