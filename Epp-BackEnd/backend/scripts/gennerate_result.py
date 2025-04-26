#对于归纳总结，我们首先需要 原问题， 拆解后的子问题， 对于每个子问题得到的回答
#利用大模型进行格式化的输出和总结（设计prompt）
import openai

server_ip = '115.190.109.233'
url = f'http://{server_ip}:20005'
model = 'zhipu-api'
openai.api_base = f'http://{server_ip}:20005/v1'
openai.api_key = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"

def aggregate_answers(main_question, api_reply=None, search_reply=None, llm_reply=None):
    print("开始生成关于这个问题的回答：" + main_question)
    api_confidence = 1
    search_confidence = 0.8
    llm_confidence = 0.6
    # 构建完整Prompt,
    prompt = f"""
    # **整合任务说明**
你是一个智能内容整合引擎，需要基于不同领域专家的反馈生成针对问题的权威、全面且逻辑连贯的最终结论。请严格遵循以下处理流程：

**输入数据**
    这是要回答的问题：{main_question}
    这是文献查找专家返回的结果: {api_reply}
    这是搜索引擎专家返回的结果: {search_reply}
    这是原生LLM专家返回的结果: {llm_reply}

**整合策略**
1. **有效性过滤**
   - 自动忽略所有空值输入
   - 当全部专家返回空值时，返回"当前问题超出知识范围"

2. **权重分配矩阵**
   |        |   文献查找专家   |   搜索引擎专家    |   原生LLM专家   |
   |--------|-----------------|-------------------|----------------|
   | 置信度  |{api_confidence}|{search_confidence}|{llm_confidence}|
   

3. **冲突消解机制**
   - 学术争议：优先采纳文献专家高置信度结论
   - 事实矛盾：交叉验证搜索引擎时间戳最新信息
   - 观点分歧：保留多元视角并标注分歧点
**最终输出**
整合各个专家结果，综合生成结论,注意只返回整合归纳结果，不要输出任何关于思考过程的描述
    """
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        if response.choices[0].message.role == "assistant":
            result = response.choices[0].message.content
            return result
    except Exception as e:
        print(f"归纳总结出错: {e}")

