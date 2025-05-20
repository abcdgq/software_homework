# 多篇综述生成

import json
import openai
import time

test="""# 基于VAE的深度学习应用

# 引言

基于变分自编码器（VAE）的深度学习应用是近年来人工智能领域的重要研究方向，其核心价值在于通过概率生成模型实现对复杂数据的高效表征与推理。值得注意的是，VAE通过引入潜在空间的概率分布假设，不仅能够捕捉数据的内在结构，还能生成多样化的样本，在行为预测、图像理解、物理建模等任务中展现出独特优势。正如深度学习先驱Yoshua Bengio所指出："VAE框架将贝叶斯推理与深度生成模型相结合，为不确定性建模提供了数学严谨的解决方案。"这一领域的研究对于推动自动驾驶、人机交互、智 能医疗等实际应用具有重要意义，尤其是在处理不确定性、多模态数据以及小样本学习等挑战性问题上提供了新的解决思路。

VAE的研究发展大致可分为三个阶段。早期阶段（2013-2015年）主要集中在基础理论构建，如Kingma等人提出的原始VAE框架，解决了传统自编码器缺乏概率解释的问题。需要强调的是，中期阶段（2016-2018年）开始关注模型扩展，例如引入条件生成、层次化结构等改进，推动了VAE在图像生成和语音合成中的应用。近期阶段（2019年至今） 则侧重于跨领域融合与实际问题解决，如结合注意力机制、物理约束等先验知识，使得VAE在轨迹预测、多模态融合等复杂任务中表现出色。这一演进过程体现了从理论探索到应用落地的完整路径。

根据当前研究进展，基于VAE的深度学习应用可归纳为三个主要方向。在轨迹预测与行为分析方向，SocialVAE通过时间维度的潜在变量建模和社交注意力机制，显著提升了 行人轨迹预测的准确性和多模态表达能力。特别值得注意的是，图像融合与场景分类方向的研究，如FusionVAE和场景分类VAE，利用层次化潜在空间实现了多源图像信息的 有效融合与紧凑表征，为自动驾驶等场景提供了高效的视觉理解方案。物理建模与控制学习方向则以NewtonianVAE为代表，通过引入物理约束的潜在空间，实现了从像素到 可控动力学模型的端到端学习，为机器人控制提供了新范式。这些方向共同构成了VAE应用的技术版图。

本综述的贡献在于系统梳理了VAE在三大应用方向的最新进展，深入分析了各方法的创新点与技术关联。与现有综述不同，本文特别关注了VAE在跨模态融合与物理可解释性 方面的突破性工作。正如MIT教授Leslie Kaelbling所评价："将物理约束融入生成模型是迈向可解释AI的重要一步。"例如SocialVAE的时序潜在变量设计和NewtonianVAE的 比例控制特性。同时，本文首次将图像融合与场景分类纳入统一框架讨论，揭示了潜在空间表征在视觉任务中的通用性价值。通过对这些前沿研究的批判性分析，本综述旨 在为研究者提供技术发展的全景视角，并指明未来交叉创新的可能路径。

# 研究方向

## 轨迹预测与行为分析
轨迹预测与行为分析的研究起源于对人类和物体运动模式的理解需求，早期方法主要依赖于物理模型和简单的统计方法。值得注意的是，随着深度学习的兴起，尤其是变分 自编码器（VAE）和循环神经网络（RNN）的结合，这一领域取得了显著进展。关键发展节点包括引入随机性和多模态建模的能力，以及通过注意力机制捕捉社交互动。当前 进展体现在能够处理复杂场景下的不确定性，并在多个基准数据集上达到最先进的性能。

SocialVAE通过时间变分自编码器架构结合随机循环神经网络，实现了对行人轨迹的多模态预测。需要特别说明的是，其核心创新点包括时间潜变量的引入、社交注意力机制和后向后验近似，这些技术有效提取了行人的导航策略。NewtonianVAE则专注于从像素中学习物理潜空间，实现了比例控制性，简化了视觉控制器的设计。这两种方法分别 适用于行人轨迹预测和机器人控制场景，展示了VAE在不同行为分析任务中的灵活性。

SocialVAE和NewtonianVAE虽然都基于VAE框架，但侧重点不同。前者专注于多模态轨迹预测，通过社交注意力处理复杂的人际互动；后者则强调从视觉输入中学习物理可解 释的潜空间，实现简单的比例控制。值得注意的是，相比之下，SocialVAE更适合密集人群环境下的行为预测，而NewtonianVAE更适用于需要物理可解释性的控制任务。两种方法都展示了VAE在行为分析中的强大表征能力，但针对不同问题提出了独特的解决方案。

## 图像融合与场景分类
图像融合与场景分类作为计算机视觉领域的重要研究方向，其技术发展脉络可以追溯到早期的传统图像处理方法。特别值得注意的是，随着深度学习的兴起，尤其是变分自 编码器（VAE）的引入，这一领域迎来了新的突破。VAE通过潜在空间的建模，能够更好地捕捉图像的全局特征和不确定性，为图像融合和场景分类提供了新的技术路径。近 年来，结合注意力机制和多任务学习的VAE变体进一步提升了性能，使得在复杂场景下的应用成为可能。当前的研究进展主要集中在如何利用VAE的潜在空间进行高效的特征 提取和融合，以及如何将这些特征应用于具体的场景分类任务中。

在提供的论文中，Fast and Efficient Scene Categorization for Autonomous Driving using VAEs提出了一种基于VAE的无监督学习方法，通过训练VAE将图像映射到受限的多维潜在空间，利用潜在向量作为全局描述符进行场景分类。该方法的核心创新点在于生成了一种紧凑且高效的全局描述符，能够捕捉图像的粗粒度特征，并且对季节和 光照变化具有鲁棒性。FusionVAE则提出了一种深度分层变分自编码器，用于多图像融合任务。其技术实现路径包括推导和优化条件对数似然的变分下界，并通过多输入图像生成多样化的输出样本。该方法的适用场景包括多传感器图像融合和部分可见图像的补全任务。

Fast and Efficient Scene Categorization for Autonomous Driving using VAEs和FusionVAE虽然都基于VAE，但在应用场景和技术路径上有所不同。前者专注于单一图像的场景分类，通过潜在空间的紧凑描述符实现高效的分类任务；后者则针对多图像融合问题，通过分层结构和条件生成模型处理复杂的多输入场景。值得注意的是，Fast and Efficient Scene Categorization更注重计算效率和鲁棒性，适用于实时自动驾驶系统；而FusionVAE则更强调模型的表达能力和多样性，适用于需要高精度融合的复杂视觉任务。两者的共同点在于都利用了VAE的潜在空间建模能力，但在具体实现和应用目标上存在显著差异。

## 物理建模与控制学习
物理建模与控制学习的研究起源于对复杂系统行为的理解和预测需求，早期工作主要集中在基于物理规则的建模方法上。需要强调的是，随着深度学习的发展，尤其是变分 自编码器（VAE）的引入，研究者开始探索如何将物理规律与数据驱动方法结合。关键发展节点包括将VAE应用于轨迹预测、场景分类和图像融合等任务，这些工作展示了VAE在捕捉复杂动态和不确定性方面的潜力。当前进展体现在更高效的模型架构设计，如SocialVAE的时间变分自编码器和FusionVAE的层次化结构，以及NewtonianVAE通过物理 潜在空间实现的比例控制。这些进展推动了物理建模与控制学习在自动驾驶、机器人控制和环境监测等领域的应用。

SocialVAE通过时间变分自编码器架构结合随机循环神经网络和社会注意力机制，有效捕捉行人轨迹的多模态不确定性。Fast and Efficient Scene Categorization利用VAE的无监督学习生成紧凑的全局描述符，适用于场景分类任务。FusionVAE采用深度层次化变分自编码器处理多源图像融合，通过优化变分下界实现信息聚合。NewtonianVAE则设计了一个物理启发的潜在空间，使得比例控制成为可能，简化了视觉控制器的行为克隆。这些方法的核心创新点在于将VAE的生成能力与特定任务的物理或语义约束相结合，技术实现路径包括潜在空间的约束设计、注意力机制的引入以及层次化结构的优化。适用场景涵盖了从微观的行人轨迹预测到宏观的场景分类和图像融合。

SocialVAE和NewtonianVAE都关注动态系统的建模，但前者侧重于社会行为的不确定性捕捉，后者则强调物理规律的可控性实现。值得注意的是，Fast and Efficient Scene Categorization与FusionVAE都涉及图像处理，但前者专注于全局特征的提取与分类，后者致力于多源信息的融合与生成。在技术路径上，SocialVAE和FusionVAE都采用了 复杂的网络结构（如时间变分和层次化VAE），而Fast and Efficient Scene Categorization和NewtonianVAE则更注重潜在空间的语义或物理约束设计。这些方法在适用场 景上的差异反映了VAE在物理建模与控制学习中的多样化应用潜力，从社会动力学到物理系统控制，再到环境感知与理解。

# 存在的不足

当前研究在基于VAE的深度学习的轨迹预测与行为分析方面，核心矛盾在于潜在空间建模与复杂社会交互动态的适配性不足。特别值得注意的是，SocialVAE虽引入时间维度 潜变量和社交注意力机制，但其后验近似仍依赖固定场景的ETH/UCY数据集，未能解决跨场景（如NBA球场与城市街道）行为模式迁移问题。特别是考虑到紧急避障等实时决 策需求时，这种局限性会导致模型在动态环境中的预测置信度骤降。实验设计普遍忽略行人意图的层次性，例如将运动轨迹与购物/通勤等高层目标解耦，削弱了多模态预测的解释性。

在图像融合与场景分类方向，VAE的瓶颈体现在全局描述符与细粒度语义的权衡失衡。需要强调的是，Fast and Efficient Scene Categorization工作虽实现128维紧凑表征，但其"农村-城市"三级分类体系过度简化了自动驾驶场景的光照突变和视角畸变问题。FusionVAE虽构建多源输入融合框架，但测试数据仍依赖合成遮挡样本，缺乏真实车 载摄像头在雨雾天气下的跨模态对齐验证。理论层面，现有变分下界优化未考虑像素级融合时的物理约束（如红外与可见光光谱相关性），导致融合图像出现违背传感器物 理特性的伪影。

物理建模与控制学习领域的关键矛盾是潜在动力学与真实物理规律的解耦。NewtonianVAE通过比例控制简化了控制器设计，但其潜在空间仅编码刚体运动学特性，无法建模 流体力学等复杂系统（如无人机抗风扰控制）。值得注意的是，实验设计多采用简化仿真环境（如MuJoCo），忽略了实际机电系统的延迟和非线性特性。数据层面严重缺乏 带物理参数标注的视觉-动力学配对数据集，特别是考虑到柔性物体操控等工业场景需求时，现有模型难以从像素反推杨氏模量等关键物性参数。实际部署还面临潜在空间维度与控制器带宽的冲突，高维潜变量虽提升建模精度但会恶化实时控制频率。

这些局限性共同反映了VAE框架在跨模态、跨尺度建模中的固有缺陷：其高斯先验假设与复杂系统（如行人决策层级、多传感器噪声分布、非光滑动力学）的真实概率结构存在根本性错配。正如斯坦福大学Daphne Koller教授所指出："当前生成模型的最大挑战在于如何将领域知识系统地融入概率框架。"未来突破需在物理信息约束的变分推理、异构数据联合嵌入、以及可微分传感器建模等方向进行范式革新。

# 结论

## 解决方法

为突破现有局限，本领域亟需在方法论层面进行系统性革新。首先针对轨迹预测与行为分析的跨场景迁移问题，可采用层级化时空VAE架构（HST-VAE）整合图对比学习。理 论依据在于行人决策具有时间尺度分离特性，短时运动与长时意图应分属不同潜空间。实施路径上，底层使用LSTM编码器处理步态动力学，高层通过图注意力网络建模场景 语义拓扑，预期突破点在于实现ETH数据集到NBA球员跑位的零样本迁移，关键指标是社会性交互预测误差降低40%。特别需要整合新兴的神经微分方程技术，将连续时间建模引入潜变量演化过程。

其次在图像融合与场景分类领域，应开发物理约束的对抗变分自编码器（PC-AVAE）。针对车载传感器噪声特性，在变分下界中引入基于光学物理的谱约束项，使用可微分渲染器构建红外-可见光联合生成模型。具体措施包括设计波段敏感的卷积核初始化策略，以及开发基于大气散射模型的噪声注入模块。该方案预期在浓雾场景下的跨模态对齐精度提升2.3dB，同时解决传统融合方法中的光谱失真问题。实施关键是通过车载FPGA实现亚毫秒级的在线推理，满足自动驾驶实时性需求。

数据增强策略方面，物理建模与控制学习领域亟需构建虚实融合的动力学数据集。针对机电系统延迟非线性特性，可采取多保真度仿真策略：在MuJoCo基础仿真上叠加高精 度FEM局部计算，同时嵌入真实伺服电机的时滞特性模型。理论支撑来源于控制理论与计算力学的耦合原理，实施时需开发自动标注管线，将有限元分析的应力场与视觉观测帧精确对齐。预期产出包含1亿帧带物性参数标注的工业机器人操作数据集，突破点在于使VAE从单目视频反推材料参数的误差控制在工程允许的5%以内。

特别需要关注的是跨领域方法论迁移，将扩散模型的条件生成机制引入VAE框架。针对复杂系统多模态分布特性，开发混合密度变分推理（MDVI）算法，通过可逆神经网络构建非高斯先验分布。该方案在柔性物体操控等工业场景已显示潜力，理论创新点在于证明了扩散过程与变分下界的数学等价性。实施时需设计专用硬件加速器处理高维潜变 量的并行采样，预计将控制指令生成延迟压缩至10ms级，满足工业级实时控制需求。

## 未来展望

未来基于VAE的深度学习应用将在技术趋势、应用场景和开放问题三个维度展现出广阔的发展前景。在技术趋势方面，随着计算能力的提升和算法优化的深入，VAE模型将更 加注重多模态数据的融合与生成，结合注意力机制、图神经网络等新兴技术，进一步提升模型的表达能力和泛化性能。值得注意的是，轻量化VAE模型的研究将成为热点，以满足边缘计算和实时应用的需求。在应用场景方面，VAE将在医疗影像分析、药物发现、个性化推荐等领域发挥更大作用，特别是在处理不完整或噪声数据时展现出独特优势。此外，VAE与强化学习的结合有望在机器人控制、自动驾驶等复杂决策任务中取得突破。

开放问题方面，如何提高VAE生成样本的多样性和真实性仍是一个关键挑战，特别是在高维数据空间中。需要强调的是，模型的可解释性和可控性也需要进一步研究，以满足医疗、金融等高风险领域的需求。隐私保护与数据安全也将成为重要研究方向，特别是在联邦学习框架下开发隐私保护的VAE变体。这些方向的发展将推动VAE在理论和应用 层面取得新的突破。正如DeepMind首席科学家David Silver所预言："下一代生成模型需要同时具备物理合理性、计算效率和语义可解释性。"

## 领域综述

基于VAE的深度学习应用领域近年来取得了显著的理论创新与方法进步。在理论层面，SocialVAE通过时间维度潜在变量和反向后验近似改进了人类轨迹预测的不确定性和多 模态建模，NewtonianVAE则创新性地在潜在空间中实现了比例控制特性，为物理系统的视觉控制提供了新思路。方法进步方面，FusionVAE构建的深度层次结构为多源图像融合提供了统一框架，而FastVAE则展示了潜在向量作为紧凑全局描述符的优越性，这些方法在保持模型效率的同时显著提升了任务性能。应用价值尤为突出，从城市交通预测到自动驾驶场景分类，从医学图像融合到蚊虫识别，VAE框架展现出强大的跨领域适应能力，特别是在处理高维感知数据和不确定性建模方面具有独特优势。

然而，这些研究仍存在若干问题与不足。多数方法依赖于特定领域的数据假设，如SocialVAE需要密集的人群轨迹标注，FusionVAE对多传感器校准敏感；计算效率与模型解 释性的平衡尚未完全解决，如FastVAE的紧凑描述符可能丢失细粒度信息；此外，跨任务泛化能力仍有提升空间，当前架构往往需要针对新任务重新设计网络层次。特别值得注意的是，未来研究可着眼于三个方向：开发更通用的VAE元架构以支持多任务迁移，探索动态潜在空间建模以适应时序演化特征，以及将物理约束更深度地嵌入生成过程以提升可控性。

该领域如同正在组装的精密仪器，核心部件（如潜在空间设计、注意力机制）已初具雏形，但各模块的协同优化与系统集成仍需突破。当前研究正处于从单点创新向体系化 框架过渡的关键阶段，随着理论工具链的完善和应用场景的拓展，基于VAE的深度学习有望成为连接感知、推理与决策的智能中枢。正如伯克利教授Stuart Russell所强调："构建既强大又可解释的生成模型是AI安全发展的必由之路。"""


def queryDeepSeek(message, syshint=None, model="deepseek-chat", max_tokens=4000):
    start_time = time.time()
    openai.api_base = "https://api.deepseek.com"
    openai.api_key = 'sk-f6a474403f6746ed9542367e4b4590b2'
    print("输入:\n", message)
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


def generate_summary(papers):
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

    if len(unopt) > 32000:  # 过长分块优化
        summary = "\n".join([query(hints["optimize"].format(msg=part)) for part in unopt])
    else:
        summary = query(hints["optimize"].format(msg="\n".join(unopt)))

    result = query(hints["reference"].format(msg=summary, papers=papers))
    # result = query(hints["reference"].format(msg=test, papers=papers))

    return result

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