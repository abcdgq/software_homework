import re
import jieba
from collections import Counter


def analyze_dialog(texts, top_n, lang='zh'):
    # 加载停用词表
    stopwords = set()
    with open('stopwords.txt', 'r', encoding='utf-8') as f:
        stopwords = {line.strip() for line in f}

    all_words = []

    for t in texts:
        # 清洗+分词
        q_clean = re.sub(r'[^\w\s]', '', t)
        words = jieba.lcut(q_clean) if lang == 'zh' else q_clean.lower().split()
        # 过滤
        filtered = [w for w in words if w not in stopwords and len(w) > 1]
        all_words.extend(filtered)

    return Counter(all_words).most_common(top_n)


# 示例用法
dialog_text = ["如何提高深度学习模型的训练效率？",
               "自然语言处理中Transformer架构有什么优势？",
               "为什么神经网络会出现过拟合现象？",
               "推荐系统常用的协同过滤算法有哪些变种？",
               "训练数据不足时如何进行有效的数据增强？",
               "在PyTorch中如何实现自定义损失函数？",
               "模型微调时应该冻结哪些网络层？",
               "知识蒸馏如何提升小模型的性能？",
               "梯度消失问题在RNN中如何解决？",
               "评估机器学习模型的常用指标有哪些？",
               "如何选择合适的学习率调度策略？",
               "分布式训练时怎样处理数据并行？",
               "对比CNN和Transformer在图像识别的差异",
               "模型量化对推理速度提升有多大帮助？",
               "自监督学习在NLP中的应用场景有哪些？",
               "如何检测文本生成模型的输出偏见？",
               "图神经网络如何处理动态关系数据？",
               "联邦学习中怎样保证数据隐私？",
               "多模态模型如何对齐视觉和语言特征？",
               "强化学习在机器人控制中的最新进展"]
results = analyze_dialog(dialog_text)
for word, freq in results:
    print(f"{word}: {freq}次")