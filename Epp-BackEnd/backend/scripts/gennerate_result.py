#对于归纳总结，我们首先需要 原问题， 拆解后的子问题， 对于每个子问题得到的回答
#利用大模型进行格式化的输出和总结（设计prompt）
import openai

server_ip = '115.190.109.233'
url = f'http://{server_ip}:20005'
model = 'zhipu-api'
openai.api_base = f'http://{server_ip}:20005/v1'
openai.api_key = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"

def aggregate_answers(main_question, child_qa_list):#TODO:微调prompt
    print(main_question)

    # 结构化子问题输入
    child_qa_str = "\n".join([
        f"- [{qa.type}] {qa.description}：{qa.result}"
        for qa in child_qa_list
    ])
    
    # 构建完整Prompt,TODO:置信度调整
    prompt = f"""
    # 任务说明
你是一个问题归纳专家，需要根据用户提供的“大问题”及其拆解后的“子问题+回答”，综合生成最终答案。子问题分为三类：
1. 查询任务(query): 需要查找特定信息或数据的问题（置信度1）
2. 总结任务(summarize): 需要对已有信息进行归纳总结的任务（置信度0.8）
3. 研读任务(study): 需要深入理解和分析复杂内容的任务（置信度0.6）

# 输入数据
- 大问题："{main_question}"
- 子问题与回答：
{child_qa_str} <-- 格式：[类型] 问题 答案 -->

# 处理步骤
1. 分类解析：逐条分析子问题类型，标注置信度等级（低/中/高）。
2. 可信度筛选：
   - 若同一事实存在多个`查询任务`答案，选择出现频率高的。
   - 若不同任务类型结论冲突，优先信任置信度高的。
3. 综合生成：
   - 整合所有子问题结论，按逻辑链条组织：
    - 核心问题表述
    - 证据链梳理（标注来源任务类型）
    - 遗留不确定性说明（来自低置信度内容）
   - 若存在`类型为summarize的总结任务`，则将总结任务的综述报告在最后输出
4. 最终输出：根据子问题的回答以及置信度等级，用简明学术语言回答大问题
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


if __name__ == '__main__':
    print(aggregate_answers(main_question = "量子计算对密码学的威胁有多大？"
, child_qa_list = [
    {"type": "查询", "question": "Shor算法当前实现需要多少量子比特？", "answer": "2023年最优实验需5000+物理量子比特"},
    {"type": "研读", "question": "分析量子计算实用化时间线对密码学的影响", "answer": "主流观点认为2035年前难以实现破解RSA的稳定量子计算机"},
    {"type": "总结", "question": "概括NIST后量子密码标准化进展", "answer": "已有4种算法进入最终标准，预计2024年发布"}
]))