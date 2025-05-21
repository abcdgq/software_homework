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
        return r
    except:
        print("没有提取到")
        return None


if __name__ =='__main__':
    get_keywords("""未来研究可能沿着三个方向突破：一是发展具有因果推理能力的结构化潜在空间，将NewtonianVAE的物理约束思想扩展到更广泛领域[14]；二是探索VAE与新型架构（如Vision Transformer）的深度融合，借鉴"蚊虫分类"研究中CNN与Transformer的混合思路[15]；三是建立跨任务的统一评估基准，解决当前各研究间评价标准不统一的问题[16] 。该领域如同正在组装的精密仪器，基础部件已初具雏形但系统集成尚待完善，正处于从理论验证向工程化应用过渡的关键阶段[17]。通过持续的理论创新与方法迭代，基 于VAE的深度学习有望成为连接感知与决策的智能中枢，为复杂系统的理解与预测提供统一框架[18]。
[1] Kingma DP, Welling M. Auto-encoding variational bayes. ICLR 2014. https://doi.org/10.48550/arXiv.1312.6114

[2] Rezende DJ, Mohamed S, Wierstra D. Stochastic backpropagation and approximate inference in deep generative models. ICML 2014;32:1278-1286. https://doi.org/10.48550/arXiv.1401.4082

[3] Higgins I, et al. beta-VAE: Learning basic visual concepts with a constrained variational framework. ICLR 2017. https://doi.org/10.48550/arXiv.1804.03599")""")