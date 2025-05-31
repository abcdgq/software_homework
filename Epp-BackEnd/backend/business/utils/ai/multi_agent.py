#这个文件存放整个多智能体流程，并向外部提供多智能体的接口get_final_answer
import concurrent.futures
import time
from business.utils.ai.agent.route_agent import generate_subtasks,get_expert_weights
from business.utils.ai.agent.api_agent import get_api_reply
from business.utils.ai.agent.search_agent import get_search_reply
from business.utils.ai.agent.llm_agent import do_file_chat
from business.utils.ai.agent.summary_agent import aggregate_answers
from business.utils.ai.agent.refine_agent import self_check

def get_final_answer(conversation_history, query, tmp_kb_id, title=None):
    q_type, subtasks = generate_subtasks(query)
    weight = get_expert_weights(q_type)
    print("多智能体：完成子问题生成")
    print(q_type, subtasks)

    print("多智能体：开始问题分发")
    if q_type == "other":
        print("other type")
        syshint = ""
        if title != None:
            syshint = f"现在我们正在进行对题目为：{title} 论文的论文研读。"
        return do_file_chat(conversation_history, syshint + query, tmp_kb_id)
    else:
        api_reply, docs_from_api,search_reply, docs_from_search,llm_reply, origin_docs, question_reply = three_api_answer(conversation_history, tmp_kb_id, subtasks)

    # 整合
    ai_reply = aggregate_answers(query, weight, api_reply, search_reply, llm_reply, title)    # 整合多专家回答
    print("多智能体：已完成问题整合")

    # 整合docs  
    for doc in docs_from_api: #规范docs格式
        origin_docs.append(" " + doc)
    for doc in docs_from_search: #规范docs格式
        origin_docs.append(" " + doc)
    docs = origin_docs
    print(origin_docs)
    # doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
    # docs.append(doc)
    print("多智能体：已完成来源整合")

    result = self_check(query, ai_reply)
    if result == None:
        result = ai_reply

    return result, docs, question_reply


def three_api_answer(conversation_history, tmp_kb_id, subtasks):
    # 使用多线程执行三个任务
    start_time = time.time()  # 记录开始时间
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 提交API任务
        api_future = executor.submit(get_api_reply, subtasks.get("api"))
        
        # 提交搜索任务
        search_future = executor.submit(get_search_reply, subtasks.get("search"))
        
        # 提交LLM任务
        print()
        llm_future = executor.submit(do_file_chat, 
                                     conversation_history, 
                                     subtasks.get("llm"), 
                                     tmp_kb_id)
        
        # 获取API结果
        api_reply, docs_from_api = api_future.result()
        
        # 获取搜索结果
        search_reply, docs_from_search = search_future.result()
        
        # 获取LLM结果
        llm_reply, origin_docs, question_reply = llm_future.result()
    
    end_time = time.time()  # 记录结束时间
    
    # 打印最终结果
    print(f"\n==== 最终结果（总耗时: {end_time - start_time:.2f}秒） ====")
    print("API回复:", api_reply)
    print("搜索回复:", search_reply)
    print("LLM回复:", llm_reply)
    print("\n引用文档:")
    print("API:", docs_from_api)
    print("搜索:", docs_from_search)
    print("LLM:", origin_docs)

    return api_reply, docs_from_api,search_reply, docs_from_search,llm_reply, origin_docs, question_reply