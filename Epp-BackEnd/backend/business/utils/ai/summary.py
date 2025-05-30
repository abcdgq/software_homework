#这个文件存放多篇综述生成的相关方法，在/scripts/summary_test.py中进行测试
import json
import time
from business.utils.ai.llm_queries.queryDeepseek import queryDeepSeek
from business.utils.ai.llm_queries.queryKimi import queryKimi

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
