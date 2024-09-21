from transformers import AutoModelForCausalLM, AutoTokenizer
import datetime
import re
from tool import GD_KEY
import json
import requests


model_name_or_path = "Qwen/Qwen2.5-1.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    torch_dtype="auto",
    device_map="auto",
)


def get_abcode(city):
    url = "https://restapi.amap.com/v3/config/district?"
    params = {
        "key": GD_KEY,
        "keywords": city,
        "subdistrict": 0,
    }
    try:
        response = requests.get(url=url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        if "1" == response.json()["status"]:
            abcode = response.json()["districts"][0]["adcode"]
            city_name = response.json()["districts"][0]["name"]
            return (abcode, city_name)
        else:
            return None
    except requests.exceptions.RequestException as e:
        # 处理请求异常
        print(f"Error during API request: {e}")
        return f"Error during API request: {e}"
    pass


def get_weather(cityname: str = "成都"):
    """Get current weather at a location.

    Args:
        cityname:获取天气的城市, in the format "City, Province".
    Returns:
        province: 省份名称,
        city: 市级城市名称,
        adcode: 城市的abcode,
        weather: 对于天气现象的描述,
        temperature: 实时气温，单位：摄氏度,
        winddirection: 风向描述,
        windpower:风力级别，单位：级,
        humidity: 空气湿度,
        reporttime: 数据发布的时间,
        temperature_float: 实时气温，单位：摄氏度 的float格式的字符串,
        humidity_float: 空气湿度 的float格式的字符串,
    """
    abcode, city_name = get_abcode(cityname)
    url = "https://restapi.amap.com/v3/weather/weatherInfo?"
    params = {"key": GD_KEY, "city": abcode, "extensions": "base"}
    try:
        # 发送请求
        response = requests.get(url=url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        if "1" == response.json()["status"]:
            return response.json()["lives"][0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return f"Error during API request: {e}"


def get_function_by_name(name):
    if name == "get_weather":
        return get_weather


tools = [get_weather]


def try_parse_tool_calls(content: str):
    """Try parse the tool calls."""
    tool_calls = []
    offset = 0
    for i, m in enumerate(re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content)):
        if i == 0:
            offset = m.start()
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"type": "function", "function": func})
            if isinstance(func["arguments"], str):
                func["arguments"] = json.loads(func["arguments"])
        except json.JSONDecodeError as e:
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")
            pass
    if tool_calls:
        if offset > 0 and content[:offset].strip():
            c = content[:offset]
        else:
            c = ""
        return {"role": "assistant", "content": c, "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"<\|im_end\|>$", "", content)}


def get_current_data():
    dt = datetime.datetime.now()
    formatted_date = dt.strftime("%Y-%m-%d")
    return formatted_date


while True:
    input_1 = input("输入问题或者，输入“结束”来结束程序\n")
    if "结束" == input_1:
        break
    dt = datetime.datetime.now()
    formatted_date = dt.strftime("%Y-%m-%d")
    MESSAGES = [
        {
            "role": "system",
            "content": f"You are Qwen, created by Alibaba Cloud. You are a helpful assistant.\n\nCurrent Date: {formatted_date}",
        },
        {
            "role": "user",
            "content": f"{input_1}",
        },
    ]
    messages = MESSAGES[:]
    text = tokenizer.apply_chat_template(
        messages, tools=tools, add_generation_prompt=True, tokenize=False
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    output_text = tokenizer.batch_decode(outputs)[0][len(text) :]
    response = try_parse_tool_calls(output_text)
    try:
        for tool_call in response.get("tool_calls", None):
            if fn_call := tool_call.get("function"):
                fn_name: str = fn_call["name"]
                fn_args: dict = fn_call["arguments"]

                fn_res: str = json.dumps(
                    get_function_by_name(fn_name)(**fn_args), ensure_ascii=False
                )
                print(f"工具测试：\n{fn_res}")

    except Exception as e:
        print(f"错误：\n{e}")
        pass
