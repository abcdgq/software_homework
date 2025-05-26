#该文件存放询问Deepseek的原子方法
import openai
import time
from business.utils.ai.ai_settings import deepseek_api_base, deepseek_api_key

def queryDeepSeek(message, syshint=None, model="deepseek-chat", max_tokens=4000):
    start_time = time.time()
    openai.api_base = deepseek_api_base
    openai.api_key = deepseek_api_key
    # print("输入:\n", message)
    print("输入长度:" + str(len(message)))
    history=[]
    if syshint:
        history.append({"role": "system", "content": syshint})
    history.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            stream=False,
            max_tokens=8000
    )
    res = response.choices[0].message.content
    # print("输出:", res)
    print("单次回答用时(ds):", time.time() - start_time)
    return res