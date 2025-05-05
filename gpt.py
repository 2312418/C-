import socket

import json
import requests
import sys
from requests.auth import HTTPBasicAuth
import time
from zhipuai import ZhipuAI
import os

RETRIES = 25
MAX_TOKENS = 1024 #最长生成长度
BETA_URL = "http://43.163.219.59:8001/beta"
MODEL = "gpt-3.5-turbo-1106"

"""

请去智谱ai的网站上注册账号，获取API_KEY，填写到55行处，形如client = ZhipuAI("12345") # API
其中，12345为你的API_KEY

"""
#backoff.on_exception(backoff.expo, (TypeError, KeyError, JSONDecodeError, ReadTimeout, ConnectionError, ConnectTimeout), max_tries=RETRIES)

def generate_answer(contexts, model=MODEL, temperature=0):
    """
    context: str
    """
    print("question context: ")
    print(contexts)
    data = {
        "model": model,
        "messages": contexts, # 格式需要为[..., {'role': 'user', 'content': '询问内容'}] 
        "max_tokens": MAX_TOKENS,
        "temperature": temperature,
        #"top_p": 1,
        #"frequency_penalty": 0.0,
        #"presence_penalty": 0.0,
        #"stop": stop
    }
    data = json.dumps(data)
    completion = requests.post(url=BETA_URL, data=data, auth=HTTPBasicAuth(username="",password=""), timeout=300).text
    # print(completion)
    completion = json.loads(completion)
    # print(completion)
    # print()
    if 'usage' not in completion:
        raise KeyError('usage')
#    return completion["choices"][0]["message"]["content"], completion["usage"]["prompt_tokens"], completion["usage"]["completion_tokens"] #返回的依次是回复内容、输入的token数量，生成的的token数量
    return completion["choices"][0]["message"]["content"]

# print(generate_answer([{'role': 'user', 'content': '你是copilot，模仿copilot补全我的笔记，你的回答内容应当可以直接连接在我的问题后面，语言逻辑很自然。不用重复我的问题，给出专家级回答。我的笔记内容：供需曲线的定义是'}]))

def gene_zhipu_response(contexts):
    #client = ZhipuAI(api_key=os.getenv("Zhipu_API_KEY")) # API
    client = ZhipuAI(api_key='77bc788b4844f7d1257561f372fd2997.7EyOxDDS8oHoqAMI') # API
 
    prompt_intro = (
        "你是一名经验丰富的金融分析师，擅长从财务数据、估值指标、行业趋势等方面进行专业分析。"
        "用户输入的是一个未完成的分析句子或关键词，你的任务是将其扩展成完整的、具有逻辑性的分析段落。"
        "回答应具备一定深度，适合出现在研究员的基本面分析笔记中，不重复原句，不引导提问，不使用教学语气。"
        "直接补全内容，语言自然、专业。以下是用户提供的内容："
    )

    response = client.chat.completions.create(
        model="glm-4",  # 可改为你的账户实际支持的模型
        messages=[
            {"role": "user", "content": prompt_intro},
            {"role": "user", "content": contexts},
        ],
    )
    print(response.choices[0].message)
    return response.choices[0].message.content

target_host = "127.0.0.1" #服务器端地址
target_port = 9000  #端口号

init_str =  "你是一名经验丰富的金融分析师，用户会输入一个术语、观点或分析句子的开头，你的任务是将其扩展为完整的逻辑分析段落，语言自然、严谨，适合研究报告或分析笔记使用。"

while True:

    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((target_host,target_port)) 

    data = client.recv(1024)

    if not data:
        break
    data = data.decode()
    print("data:", data)

    flag = False;

    while flag == False:
        try:
            # ans = generate_answer(init_str + data);
            ans = gene_zhipu_response(data);
            flag = True;
        except Exception as e:
            time.sleep(10)
            print("error:" + str(e));
            continue;

    print("ans:" + ans);
    ans = "\n" + ans
    client.send(ans.encode());

client.close()