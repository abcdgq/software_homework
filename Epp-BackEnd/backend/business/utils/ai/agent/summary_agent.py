#该文件存储多智能体中的summary_agent，用于内容整合，在scripts/test_classifyAndGenerate.py进行测试
from business.utils.ai.llm_queries.queryGLM import queryGLM

def aggregate_answers(main_question, weight, api_reply=None, search_reply=None, llm_reply=None):
    print("开始生成关于这个问题的回答：" + main_question)
    api_confidence = weight.get("api")
    search_confidence = weight.get("search")
    llm_confidence = weight.get("llm")
    print(weight)
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
        result = queryGLM(prompt)
        return result
    except Exception as e:
        print(f"归纳总结出错: {e}")
        #出错返回llm专家回答
        return llm_reply