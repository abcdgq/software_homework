# 多篇综述生成

import json
import openai
import time


def queryDeepSeek(message, syshint=None, model="deepseek-chat", max_tokens=4000):
    start_time = time.time()
    openai.api_base = "https://api.deepseek.com"
    openai.api_key = 'sk-f6a474403f6746ed9542367e4b4590b2'
    # print("输入:\n", message)
    print("输入长度:" + str(len(message)))
    history=[]
    if syshint:
        history.append({"role": "system", "content": syshint})
    history.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            stream=False,
            max_tokens=8000
    )
    res = response.choices[0].message.content
    # print("输出:", res)
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


hints = {

"system":
"""你是{theme}领域的专家，用户提供了有关这个领域的几篇论文，现在希望你通过
为这几篇论文生成综述的方式，来了解这些论文的内容以及与该领域的关系。
综述的结构为：引言、研究方向的详细分析、研究的不足与局限、解决方法、未来展望、结论。""".lstrip(),

"theme_and_directions":
"""{papers}
你是一名文献综述写作专家，以上是一些格式为[Title+Abstract]的论文，
现在需要你根据这些论文，总结这些论文的研究主题（要求为某特定领域，10字左右），并给出该主题
下的主要研究方向分类（2-3个），
以json格式返回（包括theme与directions，其中theme为字符串，directions为字符串列表）。
例如{{"theme": "xxx","directions": ["d1","d2","d3"]}}，注意请不要用json块（```json```）
包裹。""".lstrip(),

"introduction":
"""现在撰写综述引言，需包含以下要素：     
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
格式要求：以段落的格式返回结果，遵循综述写作规范。不要列举，不要用markdown格式，不要使用
**符号，不要输出与结果无关的内容。""".lstrip(),

"detailed_directions":
"""现在撰写{direction}研究方向的详细分析，请从提供的论文中提取符合这一研究方向的论文进行
后续生成。
提供的论文及内容如下{papers} 
详细分析需包含：
1.技术发展脉络:起源, 关键发展节点,当前进展
2.论文中给出的方法的实现细节：核心创新点，技术实现路径，适用场景
3.提供的论文中符合这一研究方向的论文之间方法的对比
要求：
1.以段落的格式返回结果，遵循综述写作规范。
2.注意不要列举，不要列举，不要列举，以段落的格式回答，不要用"："进行列举，不要用markdown
格式，不要使用**，不要输出与结果无关的内容。
返回格式要求：
以json格式返回，返回格式：{{"技术发展脉络": "xxx", "论文中给出的方法的实现细节": "xxx", 
"提供的论文中符合这一研究方向的论文之间方法的对比": "xxx"}}
，注意请不要用json块（```json```）包裹。""".lstrip(),

"deficiencies":
"""{papers} \n
现在请基于“{theme}”领域下关于研究方向{directions}的研究进展，结合以上论文信息，系统分析
当前研究的不足与局限，要求生成包含以下要素的段落化文本：
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
5. 避免通用描述，突出领域特殊性""".lstrip(),

"solution":
"""{deficiencies} \n
现在生成综述的解决方案部分，请基于{theme}中{directions}的已有不足分析（见上），结合领域
发展需求与前沿技术动态，提出具有突破潜力的解决方案。
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
总字数控制在对标不足分析部分的120%""".lstrip(),

"future_view":"""现在生成未来展望部分，请根据综述的主题{theme}生成对该主题的未来展望
要求：
1.从以下三个维度进行预测：技术趋势、应用场景、开放问题
2.以段落的格式返回结果，遵循综述写作规范。注意不要列举，不要列举，不要用：进行列举，不
要用markdown格式，不要使用**，不要输出与结果无关的内容。""".lstrip(),

"field_summary":
"""现在生成结论，目前生成的综述的主题为{theme}。现在我们要生成综述的结论部分，请根据提
供的论文题目和摘要生成整合这些论文的贡献并生成综述的结论：{papers}
要求：
1.用”理论创新→方法进步→应用价值→问题与不足→未来展望“模型进行呈现
2.最后用比喻总结（如：该领域如同...正处于...阶段）
3.以段落的格式返回结果，遵循综述写作规范。注意不要列举，不要列举，不要用：进行列举，不要
用markdown格式，不要使用**，不要输出与结果无关的内容。""".lstrip(),

"optimize":
"""以下是综述的全文或部分内容，请按照要求进行优化： {msg}          
优化要求：    
    1.添加过渡句（检查段落首尾衔接，添加如"值得注意的是..."等连接词）     
    2.术语统一
    3.插入领域权威的评论 
    4.修改文中语病或表达不通顺的地方，使语句符合综述报告的风格 
    5.优化后的输出结果长度控制在原文长度的105%以上
输出要求：
    按照原文结构，不要输出与综述报告无关的语句
禁止修改：  
- 原有技术细节     
- 对比分析结论     
- 文献引用关系""".lstrip(),

"reference":
"""
请执行以下添加参考文献操作（需保持原文内容绝对不变，且添加的参考文献数量小于40）：

    【任务说明】
    1. 参考文献生成：
       - 全文引用25-40篇（最多不超过40篇）
       - 综述每段引用1-5篇（最多不超过5篇）
       - 按引用顺序编号
       - 标准格式：
         [序号] 作者. 标题. 期刊/会议 缩写 年份;卷(期):起止页. DOI
       - 确保文献真实存在（可通过DOI验证）
    
    2. 引用标注：
       - 在首次提及重要概念/方法时插入数字标记[1][2]
       - 标号最大为[40],即最多40篇参考文献
       - 标注位置示例：
         "在Transformer架构中[1]..."
       - 同一文献多个位置引用使用相同编号
       - 避免在以下位置标注：
         * 背景描述段落
         * 过渡句
         * 常识性陈述
    
    3. 文献自动发现：
       - 根据技术术语、方法名称、实验结果等要素
       - 在IEEE Xplore/arXiv等权威数据库检索相关文献
       - 确保文献与上下文强相关
         
    【输入内容】
    {msg}
    【目前已经确定的参考文献】
    {papers}
    
    【约束条件】
    - 绝对禁止修改原文内容或段落结构,保持原文内容绝对不变
    - 排除参考文献后的综述主体部分的长度要大于等于输入内容的长度
    - 确保参考论文数量在40篇以内
    - 文献必须真实存在（拒绝生成虚构文献）
    
    【输出验证】
    生成后请检查：
    [1] 总文献数是否符合要求
    [2] 绝对禁止修改原文内容或段落结构,保持原文内容绝对不变
    如果有不符合条件的，请按之前的要求重新生成结果

    【输出格式】

    （修改后的内容，含引用标记）
    
    ## 参考文献
    （标准格式文献列表）

"""
}


def getQueryApplication(theme):
    def query(message, model="deepseek-chat"):
        return queryDeepSeek(
            syshint=hints["system"].format(theme=theme),
            message=message,
            model=model,
        )
    return query

import concurrent.futures

def generate_summary(papers):
    start_time = time.time()  # 记录开始时间

    data = {"papers": papers}

    # Init data starting entries: theme & directions
    theme_and_directions = queryDeepSeek(hints["theme_and_directions"].format(**data))
    data.update(json.loads(theme_and_directions))

    query = getQueryApplication(data["theme"])

    def inc_by_hint(part: str) -> str:
        res = query(hints[part].format(**data))
        data[part] = res  # `data` should take the str format
        return res
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4 + len(data["directions"])) as executor:
        # 提交所有异步任务
        futures = {
            "introduction": executor.submit(inc_by_hint, "introduction"),
            "deficiencies": executor.submit(inc_by_hint, "deficiencies"),
            "future_view": executor.submit(inc_by_hint, "future_view"),
            "field_summary": executor.submit(inc_by_hint, "field_summary"),
        }
        
        # 提交 directions 任务
        dds_f = []
        for d in data["directions"]:
            future = executor.submit(
                query,  # 直接提交query函数
                hints["detailed_directions"].format(direction=d, papers=papers)
            )
            dds_f.append(future)

        # 处理 directions 结果
        detailed_directions = []
        for i, future in enumerate(dds_f):
            res = future.result()
            r = json.loads(res)
            d = data["directions"][i]  # 通过索引获取对应方向
            detailed_directions.append("\n".join([
                f"## {d}",
                r["技术发展脉络"],
                r["论文中给出的方法的实现细节"],
                r["提供的论文中符合这一研究方向的论文之间方法的对比"],
            ]))
        data["detailed_directions"] = "\n".join(detailed_directions)
    
    mid_time = time.time()
    print(f"\n==== 优化前结果1（总耗时: {mid_time - start_time:.2f}秒） ====")

    inc_by_hint("solution")
    

    unopt = [
        """
        # {theme}

        # 引言

        {introduction}
        """.lstrip().format(**data),
        """
        # 研究方向

        {detailed_directions}
        """.lstrip().format(**data),
        """
        ## 存在的不足

        {deficiencies}
        """.lstrip().format(**data),
        """
        # 结论

        ## 解决方法

        {solution}

        ## 未来展望

        {future_view}

        ## 领域综述

        {field_summary}
        """.lstrip().format(**data),
    ]

    mid_time2 = time.time()
    print(f"\n==== 优化前结果2（总耗时: {mid_time2 - start_time:.2f}秒） ====")

    if len(unopt) > 32000:  # 过长分块优化
        summary = "\n".join([query(hints["optimize"].format(msg=part)) for part in unopt])
    else:
        summary = query(hints["optimize"].format(msg="\n".join(unopt)))

    result = query(hints["reference"].format(msg=summary, papers=papers))
    # result = query(hints["reference"].format(msg=test, papers=papers))

    end_time = time.time()  # 记录结束时间
    print(f"\n==== 优化结果（总耗时: {end_time - start_time:.2f}秒） ====")

    return result


def generate_summary2(papers):
    start_time = time.time()  # 记录开始时间

    data = {"papers": papers}

    # Init data starting entries: theme & directions
    theme_and_directions = queryDeepSeek(hints["theme_and_directions"].format(**data))
    data.update(json.loads(theme_and_directions))

    query = getQueryApplication(data["theme"])

    def inc_by_hint(part: str) -> str:
        res = query(hints[part].format(**data))
        data[part] = res  # `data` should take the str format
        return res

    inc_by_hint("introduction")

    detailed_directions = []
    for d in data["directions"]:
        r = json.loads(query(hints["detailed_directions"].format(direction=d, papers=papers)))
        detailed_directions.append("\n".join([
            f"## {d}",
            r["技术发展脉络"],
            r["论文中给出的方法的实现细节"],
            r["提供的论文中符合这一研究方向的论文之间方法的对比"],
        ]))
    data["detailed_directions"] = "\n".join(detailed_directions)

    inc_by_hint("deficiencies")
    inc_by_hint("solution")
    inc_by_hint("future_view")
    inc_by_hint("field_summary")

    unopt = [
        """
        # {theme}

        # 引言

        {introduction}
        """.lstrip().format(**data),
        """
        # 研究方向

        {detailed_directions}
        """.lstrip().format(**data),
        """
        ## 存在的不足

        {deficiencies}
        """.lstrip().format(**data),
        """
        # 结论

        ## 解决方法

        {solution}

        ## 未来展望

        {future_view}

        ## 领域综述

        {field_summary}
        """.lstrip().format(**data),
    ]

    mid_time = time.time()
    print(f"\n==== 优化前结果（总耗时: {mid_time - start_time:.2f}秒） ====")

    if len(unopt) > 32000:  # 过长分块优化
        summary = "\n".join([query(hints["optimize"].format(msg=part)) for part in unopt])
    else:
        summary = query(hints["optimize"].format(msg="\n".join(unopt)))

    result = query(hints["reference"].format(msg=summary, papers=papers))
    # result = query(hints["reference"].format(msg=test, papers=papers))

    end_time = time.time()  # 记录结束时间
    print(f"\n==== 优化结果（总耗时: {end_time - start_time:.2f}秒） ====")

    return result

def get_api_reply(api_auery):#获取本地RAG以及google scholar api检索文献结果（google scholar api有使用限制，还是以本地RAG为主）
    from test_classifyAndGenerate1 import test_localvdb_and_scholarapi #先从scripts里import，之后要把这个文件中的方法移到utils里
    return test_localvdb_and_scholarapi(api_auery)

def get_search_reply(search_query): #获取tavily搜索引擎专家的结果
    from tavily_test import tavily_advanced_search #先从scripts里import，之后要把tavily这个文件移到utils里
    search_list = tavily_advanced_search(search_query).get("results")
    # print(search_list)

    from text_summary import text_summarizer

    search_reply = ""
    docs = []
    for r in search_list:
        title = r['title']
        search_reply += f"- [{title}] "

        content = r['raw_content'] if r['raw_content'] else r['content']
        cnt = 10
        while len(content) > 2000 and cnt > 0:
            content = text_summarizer(content, cnt)
            cnt -= 1
        search_reply += f"{content}\n"

        search_reply += f"score: {r['score']}\n\n"

        docs.append(r['title'] + "   "+ r['url'])

    return search_reply, docs

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

    data = {"papers": papers}
    theme_and_directions = json.loads(queryDeepSeek(hints["theme_and_directions"].format(**data)))

    print(theme_and_directions)
    theme = theme_and_directions["theme"]

    # print(get_api_reply(f"{theme} 领域的相关论文"))
    search_reply, docs = get_search_reply(f"{theme} 领域的相关论文")
    print(search_reply)

    # print(generate_summary(papers))