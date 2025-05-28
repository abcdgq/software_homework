import json
from django.conf import settings
from business.utils.ai.llm_queries.queryGLM import queryGLM
#这个文件存储提取ai回答中需要解释的词语的相关方法，在scripts/get_keywords.py文件中进行测试

def get_keywords(answers):
    prompt = f"""现在给你一段话，请从里边提取出不多于10个专有名词并给出解释：{answers}
                注意:只能返回None或json格式，不要输出分析过程，不要输出多余的东西，不要将结果用json块包裹
                返回格式：
                    1.没有可提取的专有名词返回None
                    2.如果提取到结果就按如下json格式返回：{{"提取的专有名词1":"专有名词1的解释",}}"""
    result = queryGLM(prompt)
    print("提取的结果:\n"+result)
    try:
        r = json.loads(result)
    except:
        r = result.replace("```json", "").replace("```", "") #防止出现```json块包裹的情况
    try:
        words = []
        for w in r.keys():
            print(w)
            start = answers.find(w)
            if start == -1: #保证不会出现-1
                continue
            end = answers.find(w) + len(w)
            for ww in words:
                if start >= ww["start"] and start <= ww["end"]: 
                    start = answers.find(w, ww["end"])
                    end = start + len(w)
            if end <= len(answers):
                words.append({"start": start,
                          "end": end,
                          "word": w,
                          "tooltip": r[w]
                          })
        print(words)
        return words
    except:
        print("没有提取到")
        return []