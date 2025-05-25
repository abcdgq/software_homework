import json
import openai
from django.conf import settings

#这个文件存储提取ai回答中需要解释的词语的相关方法，在scripts/get_keywords.py文件中进行测试

def queryGLM(msg: str, history=None) -> str:
    openai.api_base = f"http://{settings.REMOTE_CHATCHAT_GLM3_OPENAI_PATH}/v1"
    openai.api_key = "none"
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


def get_keywords(answers):
    prompt = f"""现在给你一段话，请从里边提取出不多于10个专有名词并给出解释：{answers}，注意只能返回None或json，不要输出分析过程
                返回格式：
                    1.没有可提取的专有名词返回None
                    2.如果提取到结果就按如下json格式返回：{{"提取的专有名词1":"专有名词1的解释",}}"""
    result = queryGLM(prompt)
    print("提取的结果:\n"+result)
    try:
        r = json.loads(result)
        words = []
        for w in r.keys():
            words.append({"start": answers.find(w),
                          "end": answers.find(w) + len(w),
                          "word": w,
                          "tooltip": r[w]
                          })
        print(words)
        return words
    except:
        print("没有提取到")
        return []