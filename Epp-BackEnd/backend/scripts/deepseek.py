import json
import time
import openai
openai.api_base = "https://api.deepseek.com"
openai.api_key = 'sk-f6a474403f6746ed9542367e4b4590b2'
model = "deepseek-chat"

def queryDeepSeek(message):
    start_time = time.time()
    print("输入:")
    print(message)
    history=[]
    history.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            stream=False
    )
    res = response.choices[0].message.content
    print("输出:")
    print(res)
    print("单次回答用时:", time.time() - start_time)
    return res

def multi_queryDeepSeek():
    history = []
    while True:
        user_input = input("用户：")
        history.append({"role": "user", "content": user_input})
        if user_input.lower() == "exit":
            break
        print("输入长度：", len(user_input))
        print("回答：")
        response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            stream=False
        )
        res = response.choices[0].message.content
        print(res)

        json_format = json.loads(res)
        print(json_format)
        print(json_format["theme"])
        print(json_format["directions"])
        print(type(json_format))


if __name__ == '__main__':
    # message = "你好"
    # queryDeepSeek(message)
    # multi_queryDeepSeek()

    papers = """
Title:  SocialVAE: Human Trajectory Prediction using Timewise Latents
Abstract:    Predicting pedestrian movement is critical for human behavior analysis andalso for safe and efficient human-agent interactions. However, despitesignificant advancements, it is still challenging for existing approaches tocapture the uncertainty and multimodality of human navigation decision making.In this paper, we propose SocialVAE, a novel approach for human trajectoryprediction. The core of SocialVAE is a timewise variational autoencoderarchitecture that exploits stochastic recurrent neural networks to performprediction, combined with a social attention mechanism and a backward posteriorapproximation to allow for better extraction of pedestrian navigationstrategies. We show that SocialVAE improves current state-of-the-artperformance on several pedestrian trajectory prediction benchmarks, includingthe ETH/UCY benchmark, Stanford Drone Dataset, and SportVU NBA movementdataset. Code is available at: https://github.com/xupei0610/SocialVAE.

Title:  Fast and Efficient Scene Categorization for Autonomous Driving using  VAEs
Abstract:    Scene categorization is a useful precursor task that provides prior knowledgefor many advanced computer vision tasks with a broad range of applications incontent-based image indexing and retrieval systems. Despite the success of datadriven approaches in the field of computer vision such as object detection,semantic segmentation, etc., their application in learning high-level featuresfor scene recognition has not achieved the same level of success. We propose togenerate a fast and efficient intermediate interpretable generalized globaldescriptor that captures coarse features from the image and use aclassification head to map the descriptors to 3 scene categories: Rural, Urbanand Suburban. We train a Variational Autoencoder in an unsupervised manner andmap images to a constrained multi-dimensional latent space and use the latentvectors as compact embeddings that serve as global descriptors for images. Theexperimental results evidence that the VAE latent vectors capture coarseinformation from the image, supporting their usage as global descriptors. Theproposed global descriptor is very compact with an embedding length of 128,significantly faster to compute, and is robust to seasonal and illuminationalchanges, while capturing sufficient scene information required for scenecategorization.

Title:  FusionVAE: A Deep Hierarchical Variational Autoencoder for RGB Image  Fusion
Abstract:    Sensor fusion can significantly improve the performance of many computervision tasks. However, traditional fusion approaches are either not data-drivenand cannot exploit prior knowledge nor find regularities in a given dataset orthey are restricted to a single application. We overcome this shortcoming bypresenting a novel deep hierarchical variational autoencoder called FusionVAEthat can serve as a basis for many fusion tasks. Our approach is able togenerate diverse image samples that are conditioned on multiple noisy,occluded, or only partially visible input images. We derive and optimize avariational lower bound for the conditional log-likelihood of FusionVAE. Inorder to assess the fusion capabilities of our model thoroughly, we createdthree novel datasets for image fusion based on popular computer visiondatasets. In our experiments, we show that FusionVAE learns a representation ofaggregated information that is relevant to fusion tasks. The resultsdemonstrate that our approach outperforms traditional methods significantly.Furthermore, we present the advantages and disadvantages of different designchoices.

Title:  NewtonianVAE: Proportional Control and Goal Identification from Pixels  via Physical Latent Spaces
Abstract:    Learning low-dimensional latent state space dynamics models has been apowerful paradigm for enabling vision-based planning and learning for control.We introduce a latent dynamics learning framework that is uniquely designed toinduce proportional controlability in the latent space, thus enabling the useof much simpler controllers than prior work. We show that our learned dynamicsmodel enables proportional control from pixels, dramatically simplifies andaccelerates behavioural cloning of vision-based controllers, and providesinterpretable goal discovery when applied to imitation learning of switchingcontrollers from demonstration.

Title:  A Mosquito is Worth 16x16 Larvae: Evaluation of Deep Learning  Architectures for Mosquito Larvae Classification
Abstract:    Mosquito-borne diseases (MBDs), such as dengue virus, chikungunya virus, andWest Nile virus, cause over one million deaths globally every year. Becausemany such diseases are spread by the Aedes and Culex mosquitoes, tracking theselarvae becomes critical in mitigating the spread of MBDs. Even as citizenscience grows and obtains larger mosquito image datasets, the manual annotationof mosquito images becomes ever more time-consuming and inefficient. Previousresearch has used computer vision to identify mosquito species, and theConvolutional Neural Network (CNN) has become the de-facto for imageclassification. However, these models typically require substantialcomputational resources. This research introduces the application of the VisionTransformer (ViT) in a comparative study to improve image classification onAedes and Culex larvae. Two ViT models, ViT-Base and CvT-13, and two CNNmodels, ResNet-18 and ConvNeXT, were trained on mosquito larvae image data andcompared to determine the most effective model to distinguish mosquito larvaeas Aedes or Culex. Testing revealed that ConvNeXT obtained the greatest valuesacross all classification metrics, demonstrating its viability for mosquitolarvae classification. Based on these results, future research includescreating a model specifically designed for mosquito larvae classification bycombining elements of CNN and transformer architecture.
"""
    theme = "基于VAE的深度学习应用"
    directions = [
        "轨迹预测与行为分析",
        "图像分类与场景理解",
        "物理建模与控制学习"
    ]
    prompt = f"""{papers} \n
请基于以上论文的title和abstract，系统梳理当前领域研究存在的问题与不足。
要求：
1. 聚焦共性问题而非单篇论文缺陷，体现领域层面的局限性；
2. 按"现象描述-具体表现-影响分析"的逻辑展开；
3. 使用学术性语言但保持段落连贯性，避免分点编号；
4. 突出问题层级：优先方法论缺陷，其次数据/实验局限，最后理论/应用短板；

输出格式要求：
1. 直接输出成段的分析文本，不要任何引导语、标题或总结句。文本应包含以下要素：
2. 指出尚未形成共识的研究焦点
3. 揭示方法论缺陷（如实验设计、样本量、验证不足）
4. 说明数据局限性（如领域偏差、规模限制）
5. 强调理论支撑薄弱环节
6. 提及实际应用转化障碍
"""
    prompt2 = f"""{papers} \n
你是一名专业的论文分析与文献综述写作专家，请基于“{theme}”领域下关于研究方向{directions}的研究进展，结合以上论文信息，系统分析当前研究的不足与局限：

要求生成包含以下要素的段落化文本：
1. 指出该研究方向尚未突破的核心矛盾（需结合领域主题）
2. 暴露与研究方向紧密相关的方法论缺陷（如实验设计未考虑领域特性）
3. 揭示制约本方向发展的数据短板（如缺乏领域适配数据集）
4. 分析理论框架与领域需求的不匹配
5. 评估该方向实际应用转化的特殊障碍

注意：
生成的文本中不要出现markdown格式（如#，**等）
不要出现项目符号，不要出现分点数字。

输出规范：
1. 以"当前研究在{{领域主题}}的{{研究方向}}方面..."开头
2. 保持3-5个实质性观点，每观点含现象+证据+影响
3. 优先呈现阻碍研究方向发展的关键瓶颈
4. 使用"特别是考虑到...需求时"等领域关联表述
5. 避免通用描述，突出领域特殊性
"""
    deficiencies = ""
    deficiencies = queryDeepSeek(prompt2).replace("\n\n", "\n")

    prompt3 = f"""{deficiencies} \n
你是一名专业的论文分析与文献综述写作专家,请基于{theme}中{directions}的已有不足分析（见上），结合领域发展需求与前沿技术动态，提出具有突破潜力的解决方案。

注意：
生成的文本中不要出现markdown格式（如#，**等）。

生成要求：

解决方案层级
优先方法论革新（占50%内容）
其次数据增强策略（30%）
最后理论/应用创新（20%）

内容要素
每个方案需包含：
▸ 具体措施（需提及技术载体）
▸ 理论依据
▸ 实施路径
▸ 预期突破点

领域适配性
使用"针对{{领域特性}}，可采取..."的领域定制表述
至少1个方案需整合输入的趋势技术

输出规范：
以"为突破现有局限，本领域亟需..."开头
每方案用"首先/其次/特别需要"等逻辑连接词串联
禁用项目符号，保持段落连贯性
总字数控制在对标不足分析部分的120%
"""
    unreferenced = queryDeepSeek(prompt3)

    prompt4 = f"""{unreferenced} \n
请润色以上文章，为文章补充一些【真实存在的、被引用过的】参考文献并在对应位置标号（例如[1],[2,3]等），
而将对应的格式化后的参考文献单独提取到引用列表中，并使用数字编号进行标注。（如果参考文献无法格式化，则不添加在正文中添加该条参考文献）

参考文献格式样例：
1.	会议论文
格式：[序号] 作者. 文献题名[A] 论文集名[C]. 出版地:出版者, 出版年: 起止页码. 
示例：
[1] 毛峡，孙贇. 和谐图案的自动生成研究[A]. 第一届中国情感计算及智能交互学术会议论文集[C]. 北京:中国科学院自动化研究所, 2003:277-281.
[2] Mao X., Chen B., Zhu G., et al. Analysis of affective characteristics and evaluation of harmonious feeling of image based on 1/f fluctuation theory[A]. International Conference on Industrial, Engineering and Other Applications of Applied Intelligent Systems (IEA/AIE)[C]. Germany: Springer Berlin Heidelberg, 2002:780-789.
2.	期刊论文
格式：[序号] 作者.文献题名[J].刊名,出版年份,卷号(期号):起止页码.
示例：
[1] 毛峡, 丁玉宽, 牟田一弥. 图像的情感特征分析及其和谐感评价[J]. 电子学报, 2001, 29(12A):1923-1927. 
[2] Adhianto L., Banerjee S., Fagan M., et al. HPCToolkit: Tools for performance analysis of optimized parallel programs[J]. Concurrency and Computation: Practice and Experience, 2010, 22(6):685-701.
3.	学位论文
格式：[序号] 主要责任.文献题名[D].保存地:保存单位,年份. 
[1] 张和生. 地质力学系统理论[D]. 太原:太原理工大学, 1998. 
[2] Zhou X. Tiling optimizations for stencil computations[D]. Champaign:University of Illinois at Urbana-Champaign, 2013.
其他参考文献格式要求类似。

要求以json格式返回：{{"content":"润色后的正文部分，不含参考文献，只含对应标号", references":["r1", "r2"]}}，注意请不要用json块（```json```）包裹。
"""
    queryDeepSeek(prompt4)


