# 多篇综述生成

import json
import openai
import time

def queryDeepSeek(message):
    start_time = time.time()
    openai.api_base = "https://api.deepseek.com"
    openai.api_key = 'sk-f6a474403f6746ed9542367e4b4590b2'
    print("输入:\n", message)
    print("输入长度:" + str(len(message)))
    history=[]
    history.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=history,
            stream=False
    )
    res = response.choices[0].message.content
    # print("输出:")
    # print(res)
    print("单次回答用时(ds):", time.time() - start_time)
    return res

def queryKimi(message):
    start_time = time.time()
    openai.api_base = "https://api.moonshot.cn/v1"
    openai.api_key = 'sk-Nc04xpjdSvfg9q0iJQMO0nXO7iuIAhyvTo4TpbFIzVCq0bnh'
    print("输入:\n", message)
    print("输入长度:" + str(len(message)))
    history=[]
    history.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
            model="moonshot-v1-128k",
            messages=history,
            stream=False
    )
    print("单次回答用时(km):", time.time() - start_time)
    return response.choices[0].message.content

def generate_theme_and_directions(papers):
    prompt = f"""{papers}
你是一名文献综述写作专家，以上是一些格式为[Title+Abstract]的论文，
现在需要你根据这些论文，总结这些论文的研究主题（要求为某特定领域，10字左右），并给出该主题下的主要研究方向分类（2-3个），
以json格式返回（包括theme与directions，其中theme为字符串，directions为字符串列表）。
例如{{"theme": "xxx","directions": ["d1","d2","d3"]}}，注意请不要用json块（```json```）包裹。"""
    res = queryDeepSeek(prompt)
    try:
        json_format = json.loads(res)
        print("解析成功")
    except:
        print("解析失败")
        res = res.replace("```json", "").replace("```", "")
        json_format = json.loads(res)
        print("解析2成功")
    print(json_format)
    return json_format

def generate_introduction(theme, directions, papers):
    prompt = f"""撰写综述引言，需包含以下要素：     
        1.领域重要性 
        2.问题发展脉络
        3. 现有方法分类（基于提供文献的内容和提供的研究方向分类进行生成）       
        4. 本综述贡献       
    综述主题：{theme}
    研究方向分类：{directions}   
    文献内容：{papers}          
    内容要求：     
        第一段：领域背景+研究价值     
        第二段：历史发展（分阶段说明）     
        第三段：根据提供的文献内容详细阐述综述的几个研究方向    
        第四段：本综述贡献
    格式要求：以段落的格式返回结果，遵循综述写作规范。不要列举，不要用markdown格式，不要使用**，不要输出与结果无关的内容。"""
    result = queryKimi(prompt)
    print("引言：\n", result)
    return result

def generate_detailed_directions(directions, papers):
    import json
    result = ""
    for direction in directions:
        result += f"## {direction}\n"
        prompt=f"""撰写{direction}研究方向的详细分析，请从提供的论文中提取符合这一研究方向的论文进行后续生成。
                   提供的论文及内容如下{papers} 
                详细分析需包含：
                    1.技术发展脉络:起源, 关键发展节点,当前进展
                    2.论文中给出的方法的实现细节：核心创新点，技术实现路径，适用场景
                    3.提供的论文中符合这一研究方向的论文之间方法的对比
	            要求：
                    1.以段落的格式返回结果，遵循综述写作规范。
                    2.注意不要列举，不要列举，不要列举，以段落的格式回答，不要用"："进行列举，不要用markdown格式，不要使用**，不要输出与结果无关的内容。
                返回格式要求：
                    以json格式返回，返回格式：{{"技术发展脉络": "xxx", "论文中给出的方法的实现细节": "xxx", "提供的论文中符合这一研究方向的论文之间方法的对比": "xxx"}}
                """
        result_in_json = queryKimi(prompt)
        r = json.loads(result_in_json)
        result += r["技术发展脉络"] + "\n" + r["论文中给出的方法的实现细节"] + "\n" + r["提供的论文中符合这一研究方向的论文之间方法的对比"] + "\n"
    print("研究方向: \n", result)
    return result

def generate_deficiencies(theme, directions, papers):
    prompt = f"""{papers} \n
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
    result = queryDeepSeek(prompt)
    print("存在不足：\n", result)
    return result

def generate_solution(theme, directions, deficiencies):
    prompt = f"""{deficiencies} \n
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
    result = queryDeepSeek(prompt)
    print("结论1：\n", result)
    return result

def generate_future_view(theme):
    prompt=f"""根据综述的主题{theme}生成对该主题的未来展望
				要求：
                1.从以下三个维度进行预测：技术趋势、应用场景、开放问题
                2.以段落的格式返回结果，遵循综述写作规范。注意不要列举，不要列举，不要用：进行列举，不要用markdown格式，不要使用**，不要输出与结果无关的内容。"""
    result = queryKimi(prompt)
    print("结论2: \n", result)
    return result

def generate_field_summary(theme, papers):
    prompt=f"""目前生成的综述的主题为{theme}。现在我们要生成综述的结论部分，请根据提供的论文题目和摘要生成整合这些论文的贡献并生成综述的结论：{papers}
			   要求：
                1.用”理论创新→方法进步→应用价值→问题与不足→未来展望“模型进行呈现
                2.最后用比喻总结（如：该领域如同...正处于...阶段）
                3.以段落的格式返回结果，遵循综述写作规范。注意不要列举，不要列举，不要用：进行列举，不要用markdown格式，不要使用**，不要输出与结果无关的内容。"""
    result = queryKimi(prompt)
    print("结论3：\n", result)
    return result

def generate_conclusion(theme, directions, papers, deficiencies):
    solution = generate_solution(theme, directions, deficiencies)
    future_view = generate_future_view(theme)
    field_summary = generate_field_summary(theme, papers)
    return f"## 弥补不足\n{solution}\n## 未来展望\n{future_view}\n## 领域综述\n{field_summary}\n"

def generate_summary(papers):
    themes = generate_theme_and_directions(papers)
    theme = themes["theme"]
    directions = themes["directions"]
    introduction = generate_introduction(theme, directions, papers)
    detailed_directions = generate_detailed_directions(directions, papers)
    deficiencies = generate_deficiencies(theme, directions, papers)
    conclusion = generate_conclusion(theme, directions, papers, deficiencies)
    summary = f"# {theme}" + "\n# 引言\n" + introduction + "\n# 研究方向\n" + detailed_directions
    summary += "\n##存在的不足\n" + deficiencies + "\n# 结论\n" + conclusion
    return summary

if __name__ == "__main__":
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
    print(generate_summary(papers))