#该文件存储多智能体中的route_agent，用于实现子问题的分发，在scripts/routing_agent.py进行测试
import json
from business.utils.ai.llm_queries.queryGLM import queryGLM

TYPE_WEIGHTS = {
    "definition": {"api": 0.6, "search": 0.2, "llm": 0.2},
    "principle": {"api": 0.4, "search": 0.3, "llm": 0.3},
    "implementation": {"api": 0.3, "search": 0.5, "llm": 0.2},
    "comparison": {"api": 0.5, "search": 0.3, "llm": 0.2},
    "application": {"api": 0.3, "search": 0.6, "llm": 0.1},
    "default": {"api": 0.4, "search": 0.4, "llm": 0.2}
}

Q_TYPE = ["definition", "principle", "implementation", "comparison", "application"] # 定义 原理 实现 对比 应用


def extract_keywords(query: str) -> list:
        """提取问题关键词"""
        # prompt = f"""
        # 请从以下问题中提取最多3个技术关键词，按重要性排序：
        # 问题：{query}
        # 要求：只返回用空格分隔的词语，不要任何解释
        # 注意：如果没有提取到关键字，请直接返回，不要返回多余内容
        # 当问题为类似"?"等与科研内容无关内容时，视为无关键字处理
        # 示例：如果问题是"什么是VQ-VAE"，应返回"VQ-VAE 定义 生成模型"
        # """
        prompt = f"""
        请从以下问题中提取技术相关关键词，遵循规则：
        1. 最多返回3个关键词，按重要性排序
        2. 若无合适关键词，返回空列表
        3. 必须使用严格JSON格式：{{"keywords": [...]}}

        示例1：
        输入："什么是VQ-VAE？"
        输出：{{"keywords": ["VQ-VAE", "生成模型", "向量量化"]}}

        示例2：
        输入："请解释这篇论文的主要贡献"
        输出：{{"keywords": []}}

        当前问题：{query}
        """
        try:
            response = queryGLM(prompt)
            result = json.loads(response)
            if isinstance(result.get("keywords"), list):
                # 过滤空字符串和非字符串项
                return [str(kw) for kw in result["keywords"] if kw and isinstance(kw, (str, int, float))][:3]
        except Exception as e:
            return []


def classify_question_type(query: str) -> str:
        """问题类型分类"""
        prompt = f"""
        判断以下问题的类型（单选）：
        [选项] {" / ".join(Q_TYPE)}
        问题：{query}
        要求：只需返回单个类型标签，无需额外内容。
        注意：若问题中没有包含任何与学术科研相关的词，可认为该问题与科研无关，此时返回"other"
        示例：若问题是"什么是VQ-VAE"，应返回"definition"
        """
        q_type = queryGLM(prompt).strip()
        return q_type if q_type in Q_TYPE else "other"

def get_expert_weights(q_type: str) -> dict:
    """获取专家权重配置"""
    return TYPE_WEIGHTS.get(q_type, TYPE_WEIGHTS["default"])

def get_api_expert_weight(q_type: str) -> float:
    return get_expert_weights(q_type)["api"]

def get_search_expert_weight(q_type: str) -> float:
    return get_expert_weights(q_type)["search"]

def get_llm_expert_weight(q_type: str) -> float:
    return get_expert_weights(q_type)["llm"]


def generate_subtasks(query: str) -> dict:
        """手动生成专家子任务"""
        q_type = classify_question_type(query)
        
        if q_type == "other":
            return q_type, {
                "llm": query
            }
        else:
            keywords = extract_keywords(query)
            if len(keywords) > 0:
                return q_type, {
                    "api": ' '.join(keywords),
                    "search": query,
                    "llm": query
                }
            else:
                return "other", {
                    "llm": query
                }
        
def generate_subtasks_2(paper_title: str, query: str) -> dict:
        """AI生成专家子任务"""
        keywords = extract_keywords(query)
        q_type = classify_question_type(query)
        
        # 构造分发prompt
        prompt = f"""
        你是一个论文研读助手的分发系统，当前用户正在阅读论文《{paper_title}》。
        用户问题：{query}
        
        需要将问题拆解为三个子任务，分别分配给以下专家：
        1. API专家 - 负责通过学术数据库查询权威信息
        2. 搜索引擎专家 - 负责查找实际应用和最新动态
        3. 原生LLM专家 - 负责理论解释和逻辑推理
        
        请根据问题类型【{q_type}】和关键词【{', '.join(keywords)}】：
        - 为每个专家生成对应的子问题
        - 确保子问题之间互补不重复
        - 用中文表述子问题
        
        返回严格的JSON格式：
        {{
            "subtasks": {{
                "api_expert": "API专家的子问题描述",
                "search_expert": "搜索引擎专家的子问题描述",
                "llm_expert": "LLM专家的子问题描述"
            }}
        }}
        """
        
        try:
            result = json.loads(queryGLM(prompt))
            return {
                "problem_type": q_type,
                "keywords": keywords,
                "subtasks": {
                    "api": result["subtasks"]["api_expert"],
                    "search": result["subtasks"]["search_expert"],
                    "llm": result["subtasks"]["llm_expert"]
                }
            }
        except Exception as e:
            return generate_fallback_subtasks(query, q_type, keywords, paper_title)
        
def generate_fallback_subtasks(query: str, q_type: str, keywords: list, paper_title: str) -> dict:
        """备选方案：当大模型输出不符合格式时"""
        if len(keywords) > 0:
            keyword = keywords[0]
        else:
            print("No keywords found, using 'none' as fallback.")
            keyword = "none"
        keyword = keywords[0]

        task_mapping = {
            "definition": {
                "api": f"查询《{paper_title}》中关于{keyword}的正式定义",
                "search": f"查找{keyword}的最新应用案例",
                "llm": f"解释{keyword}的核心概念"
            },
            "principle": {
                "api": f"检索{keyword}的技术原理论文",
                "search": f"查找{keyword}的实现流程图",
                "llm": f"逐步说明{keyword}的工作原理"
            },
            "implementation": {
                "api": f"搜索{keyword}在顶会论文中的实现细节",
                "search": f"查找GitHub上{keyword}的高星实现项目",
                "llm": f"描述{keyword}的核心算法流程"
            },
            "comparison": {
                "api": f"获取{keyword}与其他方法的对比研究论文",
                "search": f"查找技术社区对{keyword}的优缺点讨论",
                "llm": f"分析{keyword}与竞品的性能差异原因"
            },
            "application": {
                "api": f"查询{keyword}在特定领域（如医疗/金融）的应用论文",
                "search": f"查找{keyword}的实际部署案例和技术博客",
                "llm": f"解释{keyword}适合解决的问题场景"
            },
            # 其他类型映射...
        }
        return task_mapping.get(q_type, {
            "api": f"关于'{query}'的学术文献查询",
            "search": f"关于'{query}'的相关研究搜索",
            "llm": f"解释'{query}'的核心要点"
        })
