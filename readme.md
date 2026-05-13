1. 创建新的虚拟环境：
```bash
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process RemoteSigned
..venv\Scripts\Activate.ps1
```
2. 安装依赖：
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```
3. 复制环境变量文件并填写 DeepSeek 配置：
```bash
Copy-Item .envexample .env
notepad .env
```
其中配置文件修改为：
```text
NO_PROXY=localhost,127.0.0.1
DEEPSEEK_API_KEY=你的key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```
4. 运行方法: 
```bash
python main.py
```
最终输出统一位于output文件夹里。

main.py中的project_root、tools中的一些路径要改（已改为相对路径）

agent0~5可以各自测试
