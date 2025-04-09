import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
import pandas as pd


def generate_standard_answer(questions):
    """
    根据一组相似问题自动生成标准化回答

    参数：
    - questions (list): 相似问题列表

    返回：
    - str: 生成的标准化回答
    """
    # 提取问题中的共同关键词（简单实现）
    words = []
    for q in questions:
        words.extend(q.replace("？", "").split())
    common_words = [word for word in set(words) if words.count(word) > 1]

    if len(questions) == 1:
        return f"关于'{questions[0]}'，建议您查看相关帮助文档获取详细信息。"
    elif common_words:
        topic = "、".join(common_words[:3])  # 最多取3个关键词
        examples = "，".join([f"'{q}'" for q in questions[:3]])
        return f"针对{topic}相关问题（如{examples}），我们的解答是：这些问题都与{topic}相关，具体信息请参考相关文档。"
    else:
        examples = "，".join([f"'{q}'" for q in questions[:3]])
        return f"针对以下相关问题：{examples}，这些问题属于同一类别，建议查阅我们的常见问题解答。"


def cluster_questions(questions, model_name='paraphrase-multilingual-MiniLM-L12-v2', eps=0.5, min_samples=2):
    """
    对用户问题进行聚类，并自动生成标准化回答

    参数：
    - questions (list): 用户问题列表
    - model_name (str): 使用的Sentence-BERT模型
    - eps (float): DBSCAN的邻域距离阈值
    - min_samples (int): 形成核心点所需的最小样本数

    返回：
    - tuple: (聚类结果DataFrame, 标准化回答字典)
    """
    # 1. 加载模型并生成嵌入
    model = SentenceTransformer(model_name)
    embeddings = model.encode(questions)
    embeddings = normalize(embeddings, axis=1)

    # 2. 计算相似度并聚类
    cos_sim = util.pytorch_cos_sim(torch.tensor(embeddings), torch.tensor(embeddings))
    distance_matrix = np.maximum(1 - cos_sim.numpy(), 0)

    db = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
    labels = db.fit_predict(distance_matrix)

    # 3. 组织结果
    results = pd.DataFrame({'question': questions, 'cluster_id': labels})

    # 4. 为每个聚类生成回答
    standard_answers = {}

    # 先处理噪声点（cluster_id = -1）
    noise_questions = results[results['cluster_id'] == -1]['question'].tolist()
    for i, question in enumerate(noise_questions):
        standard_answers[f"noise_{i}"] = {
            'type': '独立问题',
            'question': question,
            'answer': f"关于'{question}'，这是一个特定问题，建议直接咨询客服获取详细解答。"
        }

    # 处理正常聚类（cluster_id >= 0）
    for cluster_id, group in results[results['cluster_id'] != -1].groupby('cluster_id'):
        cluster_questions = group['question'].tolist()
        standard_answer = generate_standard_answer(cluster_questions)

        standard_answers[cluster_id] = {
            'type': f'聚类 {cluster_id}',
            'questions': cluster_questions,
            'answer': standard_answer,
            'cluster_size': len(cluster_questions)
        }

    return results, standard_answers


# 示例使用
if __name__ == "__main__":
    questions = [
        # 基础概念相似问题
        "什么是计算机视觉？",
        "计算机视觉的定义是什么？",
        "请解释计算机视觉的含义。",
        "计算机视觉的核心概念是什么？",

        # # 模型架构相似问题
        # "卷积神经网络（CNN）在计算机视觉中的作用是什么？",
        # "CNN在计算机视觉中的主要功能是什么？",
        # "卷积神经网络如何应用于计算机视觉？",
        # "计算机视觉中卷积神经网络的作用是什么？",
        #
        # 目标检测相似问题
        "目标检测算法有哪些经典模型？",
        "经典的目标检测算法有哪些？",
        "目标检测领域的主流模型有哪些？",
        "请列举目标检测的代表性算法。",

        # # 语义分割相似问题
        # "语义分割和实例分割的区别是什么？",
        # "语义分割与实例分割的核心差异是什么？",
        # "实例分割和语义分割的对比是什么？",
        # "请解释语义分割和实例分割的区别。",
        #
        # # 最新进展相似问题
        # "2023年计算机视觉领域有哪些重要突破？",
        # "2023年计算机视觉的最新进展是什么？",
        # "2023年计算机视觉领域的突破性研究有哪些？",
        # "计算机视觉在2023年的最新成果是什么？",
        #
        # # 实践应用相似问题
        # "如何用Python实现一个简单的图像分类模型？",
        # "使用Python实现图像分类模型的步骤是什么？",
        # "请说明如何用Python构建图像分类模型。",
        # "Python实现图像分类模型的方法是什么？",
        #
        # # 行业趋势相似问题
        # "未来5年计算机视觉的主要发展方向是什么？",
        # "计算机视觉未来5年的重点发展方向是什么？",
        # "未来5年计算机视觉领域的趋势是什么？",
        # "请预测计算机视觉未来5年的发展方向。"
    ]

    results, standard_answers = cluster_questions(questions)

    print("=== 聚类结果 ===")
    print(results)

    print("\n=== 标准化回答 ===")
    for key, answer in standard_answers.items():
        print(f"\n[{answer['type']}]")
        if 'questions' in answer:
            print(f"共{answer['cluster_size']}个类似问题")
            print("代表问题:", "，".join(answer['questions'][:3]))
        else:
            print("问题:", answer['question'])
        print("回答:", answer['answer'])

