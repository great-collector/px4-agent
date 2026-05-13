前端依赖要求：
- Flask (>=2.0.0)

启动步骤
1：激活虚拟环境

cd C:\Users\sysu\Desktop\px4_agent\px4-agent
.\.venv\Scripts\Activate.bat

2：检查并安装依赖

安装指令（只需执行一次）：
pip install flask -i https://mirrors.aliyun.com/pypi/simple/

检查指令：
python -m pip show flask

3：进入前端目录并启动服务

cd frontend
python app.py