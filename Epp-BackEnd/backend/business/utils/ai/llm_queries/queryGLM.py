#该文件存放询问服务器ai的原子方法（一次对话）
import openai
from business.utils.ai.ai_settings import glm_api_base, glm_api_key

def queryGLM(msg: str, history=None) -> str:
    openai.api_base = glm_api_base
    openai.api_key = glm_api_key
    if history is None:
        history = [{'role' : 'user', 'content': msg}]
    else:
        history.extend([{'role' : 'user', 'content': msg}])
    response = openai.ChatCompletion.create(
        model="zhipu-api",
        messages=history,
        stream=False
    )
    return response.choices[0].message.content