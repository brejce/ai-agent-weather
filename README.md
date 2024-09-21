# ai-agent-weather
使用大模型ai-qwen2-1.5b 来查询真实的天气，极简版。


# 首先安装 环境

- 你需要安装最新的python环境，和vscode编辑器。
- 打开vscode，新建一个文件夹，在文件夹新建一个 main.py 文件，右下角点击选择解释器，选择python。
- 前面2个步骤在其他很多关于python的教材里面都是有的。进阶可以选择建立虚拟的python环境，例如venv。
- 安装 torch accelerate transformers，直接在命令行使用 pip install torch accelerate transformers,即可安装好所需要的环境。
- 获取高德天气api所需要的key。搜索 高德开放平台 找到web服务api 进入开发指南，选择基础api文档，选择行政区域查询，找到使用说明，工具说明获取web服务api的密钥key。


# 编写并运行代码，
  根据对官方文档 https://qwen.readthedocs.io/zh-cn/latest/framework/function_call.html#id3 对函数调用的描述。
  编写对应的代码。

# 运行代码
