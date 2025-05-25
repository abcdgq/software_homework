import openai

openai.api_base = "https://api.moonshot.cn/v1"
openai.api_key = 'sk-Nc04xpjdSvfg9q0iJQMO0nXO7iuIAhyvTo4TpbFIzVCq0bnh'

def queryKimi(message):
    print("输入:")
    print(message)
    history=[]
    user_input=message
    history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
            model="moonshot-v1-128k",
            messages=history,
            stream=False
    )
    res = response.choices[0].message.content
    print("输出:")
    print(res)
    return res

def multi_queryKimi():
    history = []
    while True:
        user_input = input("用户：")
        history.append({"role": "user", "content": user_input})
        if user_input.lower() == "exit":
            break
        print("输入长度：", len(user_input))
        print("回答：")
        response = openai.ChatCompletion.create(
            model="moonshot-v1-128k",
            messages=history,
            stream=False
        )
        res = response.choices[0].message.content
        print(res)

if __name__ == '__main__':
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

输出规范：
1. 以"当前研究在{{领域主题}}的{{研究方向}}方面..."开头
2. 保持3-5个实质性观点，每观点含现象+证据+影响
3. 优先呈现阻碍研究方向发展的关键瓶颈
4. 使用"特别是考虑到...需求时"等领域关联表述
5. 避免通用描述，突出领域特殊性
"""
    deficiencies = """
当前研究在基于VAE的深度学习应用的轨迹预测与行为分析、图像分类与场景理解、物理建模与控制学习方面，尽管取得了一定的进展，但仍存在一些核心矛盾和局限性。

首先，在轨迹预测与行为分析方面，当前研究尚未突破的核心矛盾在于如何准确捕捉和建模行人的不确定性和多模态行为。例如，SocialVAE虽然通过时间化的变分自编码器和社交注意力机制提高了预测性能，但仍然难以完全捕捉行人行为的复杂性和多样性。特别是考虑到安全和高效的人际交互需求时，现有方法在处理复杂场景和动态环境中的行人行为预测方面仍存在局限性。

其次，在图像分类与场景理解方面，当前研究的方法论缺陷主要体现在实验设计上。例如，Fast and Efficient Scene Categorization for Autonomous Driving using VAEs主要关注于生成紧凑的全局描述符，而忽视了场景理解中的细节信息和上下文信息。这导致模型在处理复杂场景和动态变化时，难以准确捕捉场景的细微差别和变化，影响了分类和理解的准确性。

再次，在物理建模与控制学习方面，当前研究制约发展的数据短板主要体现在缺乏领域适配的数据集。例如，NewtonianVAE虽然提出了一种新的物理建模框架，但缺乏大规模、高质量的物理交互 数据集来训练和验证模型。这限制了模型的泛化能力和实际应用价值，特别是在需要精确控制和目标识别的复杂任务中。

此外，当前研究的理论框架与领域需求之间存在不匹配。例如，FusionVAE虽然提出了一种新的深度层次化变分自编码器，但其主要关注于图像融合任务，而忽视了领域特有的需求，如实时性和鲁棒性。这导致模型在实际应用中难以满足领域特有的性能要求。

最后，在实际应用转化方面，当前研究面临一些特殊障碍。例如，A Mosquito is Worth 16x16 Larvae: Evaluation of Deep Learning Architectures for Mosquito Larvae Classification虽 然提出了一种新的基于ViT的分类模型，但其主要关注于模型性能的比较，而忽视了模型部署和应用的实际挑战，如计算资源限制和实时性要求。这限制了模型在实际场景中的应用潜力和价值。  

综上所述，当前基于VAE的深度学习应用研究在轨迹预测与行为分析、图像分类与场景理解、物理建模与控制学习等方面，仍存在一些核心矛盾和局限性。未来研究需要进一步探索和突破这些瓶颈，以推动该领域的持续发展和应用。
""".replace("\n\n", "\n")

    prompt3 = f"""{deficiencies} \n
你是一名专业的论文分析与文献综述写作专家,请基于{theme}中{directions}的已有不足分析（见上），结合领域发展需求与前沿技术动态，提出具有突破潜力的解决方案。

生成要求：

解决方案层级
优先方法论革新（占50%内容）
其次数据增强策略（30%）
最后理论/应用创新（20%）

内容要素
每个方案需包含：
▸ 具体措施（需提及技术载体）
▸ 理论依据（引用≥2篇论文的发现）
▸ 实施路径（如"通过融合X论文的A方法与Y论文的B框架"）
▸ 预期突破点（量化描述如"有望提升XX指标15-20%"）

领域适配性
使用"针对{{领域特性}}，可采取..."的领域定制表述
至少1个方案需整合输入的趋势技术

输出规范：
以"为突破现有局限，本领域亟需..."开头
每方案用"首先/其次/特别需要"等逻辑连接词串联
禁用项目符号，保持段落连贯性
总字数控制在对标不足分析部分的120%
"""

    # queryKimi(prompt2)
    queryKimi(prompt3)
    