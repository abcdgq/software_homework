#该文件存储多智能体中的llm_agent，用于进行原生llm专家的对话
#原本在paper_interpret.py中是do_file_chat方法，在search.py中是kb_ask_ai方法。
#虽两个方法内部实现不同，但功能完全一样，do_file_chat仅多返回了一个推荐问题，所以最后为了保证统一，决定使用do_file_chat方法。
import json
import requests
import re
from django.conf import settings

def do_file_chat(conversation_history, query, tmp_kb_id):
    print("do_file_chat")
    file_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/file_chat'
    headers = {
        'Content-Type': 'application/json'
    }

    # 构建请求 payload
    if len(conversation_history) != 0:
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "history": conversation_history[-10:],  # 传10条历史记录
            "prompt_name": "text",  # 使用历史记录对话模式
            "max_tokens": 500,
        })
    else:
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "prompt_name": "default",  # 使用普通对话模式
            "max_tokens": 500,
        })

    # print(f"Sending payload to server: {payload}")

    def _get_ai_reply(payload):
        try:
            # 发送请求
            response = requests.post(file_chat_url, data=payload, headers=headers, stream=True)
            # 检查 HTTP 请求是否成功
            response.raise_for_status()

            ai_reply = ""
            origin_docs = []

            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    # print(f"Received line: {decoded_line}")

                    if decoded_line.startswith('data'):
                        data = decoded_line.replace('data: ', '')
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse JSON: {e}")
                            print(f"Invalid JSON data: {data}")
                            raise

                        ai_reply += data.get("answer", "")
                        for doc in data.get("docs", []):
                            doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
                            origin_docs.append(doc)

            return ai_reply, origin_docs

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Response status code: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"Response content: {response.content if 'response' in locals() else 'N/A'}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    try:
        ai_reply, origin_docs = _get_ai_reply(payload)
    except Exception as e:
        print(f"Failed to get AI reply: {e}")
        raise

    def _get_prob_paper_study_question():
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "history": conversation_history[-4:],
            "prompt_name": "question",  # 使用问题模式
            "max_tokens": 50,
            "temperature": 0.4
        })

        # print(f"Sending question payload to server: {payload}")

        try:
            question_reply, _ = _get_ai_reply(payload)
            # question_reply = question_reply.replace("\n\n", "\n")   # 避免两次换行
            question_reply = re.sub(r'\d. ', '', question_reply).split("\n")[:2]
            question_reply.append("告诉我更多")
            return question_reply
        except Exception as e:
            print(f"Failed to get study question: {e}")
            raise

    try:
        question_reply = _get_prob_paper_study_question()
    except Exception as e:
        print(f"Failed to generate study questions: {e}")
        question_reply = ["发生错误，请稍后再试", "告诉我更多"]

    return ai_reply, origin_docs, question_reply