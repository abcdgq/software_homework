import json
import openai

def queryGLM(msg: str, history=None) -> str:
    openai.api_base = 'http://115.190.109.233:20005/v1'
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
            start = answers.find(w)
            end = answers.find(w) + len(w)
            for ww in words: #避免出现解释词包含在已解释词中
                if answers.find(w) >= ww["start"] and answers.find(w) <= ww["end"]: 
                    start = answers.find(start=ww["end"])
                    end = start + len(w)
            if end <= len(answers) and start <= end:
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


if __name__ =='__main__':
    get_keywords("""变分自编码器，简称VAE，主要应用于无监督学习的深度学习技术，并在生成模型领域表现出色。该模型融合了自编码器与概率图模型中的变分推断技术，其中编码器将输入数据转换至潜在空间，并以参数形式，如潜在变量的均值和方差来表示；解码器则将这些参数还原至原始数据形态。综合权重分配矩阵和冲突消解机制所提供的信息，我们得知DC-VAE作为VAE的一种先进形式，通过结合实例级判别损失与集合级对抗损失，显著提高了图像处理和表示学习的性能，成为适用于众多下游任务的强大VAE模型。此外，VAE的原理在机器学习中得到应用，并与其自编码器的根基紧密相连。在无监督学习方面，VAE的图像重建和合成能力尤其值得关注。因此，VAE及其改进型DC-VAE，因其在生成模型工具中的通用性和灵活性，成为了计算机视觉和机器学习领域中不可或缺的技术。""")