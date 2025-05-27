#该文件存储多智能体中的refine_agent，用于对结果进行自反思，优化回答结果
import json
from business.utils.ai.llm_queries.queryGLM import queryGLM

def self_check(query, reply):
    # 2. 自反馈机制
    # 2.1 检查回答质量
    # 2.2 TODO 可以持久化检测报告，返回给多智能体，从而实现自反馈
    ai_reply = reply
    quality_check_prompt = f"""
       请评估以下回答的质量，指出存在的问题：
       问题：{query}
       回答：{ai_reply}

       评估标准：
       1. 准确性 - 信息是否准确无误
       2. 完整性 - 是否全面回答了问题
       3. 清晰度 - 表达是否清晰易懂
       4. 相关性 - 内容是否紧密围绕问题

       请按以下格式返回评估结果：
       {{
           "accuracy": 评分(1-5),
           "completeness": 评分(1-5),
           "clarity": 评分(1-5),
           "relevance": 评分(1-5),
           "issues": ["具体问题描述1", "具体问题描述2"]
       }}
       """

    quality_report = queryGLM(quality_check_prompt)
    print("质量评估报告:", quality_report)

    try:
        quality_data = json.loads(quality_report)
        # 如果任何一项评分低于3分，则进行修正
        if any(score < 3 for score in [quality_data["accuracy"], quality_data["completeness"],
                                       quality_data["clarity"], quality_data["relevance"]]):
            print("检测到低质量回答，正在进行修正...")
            correction_prompt = f"""
               原始问题：{query}
               初始回答：{ai_reply}
               检测到的问题：{quality_data["issues"]}

               请根据以下要求改进回答：
               1. 修正不准确的信息
               2. 补充缺失的重要内容
               3. 使表达更加清晰专业
               4. 保持回答简洁明了
               5. 保持专业学术风格
               6. 修正语法和表达错误
               7. 优化段落结构
               8. 保持原意的完整性
               返回改进后的回答
               """
            ai_reply = queryGLM(correction_prompt)
            print("修正后的回答:", ai_reply)
            return ai_reply
    except:
        print("质量评估解析失败，使用原始回答")
        return reply
    