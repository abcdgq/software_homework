#该文件存放询问Kimi的原子方法
import openai
from business.utils.ai.ai_settings import kimi_api_base, kimi_api_key

def queryKimi(message):
    history=[]
    openai.api_base = kimi_api_base
    openai.api_key = kimi_api_key
    user_input=message
    history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
            model="moonshot-v1-128k",
            messages=history,
            stream=False
    )
    res = response.choices[0].message.content
    return res