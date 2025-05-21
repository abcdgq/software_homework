import openai
openai.api_base = "https://api.deepseek.com"
openai.api_key = 'sk-f6a474403f6746ed9542367e4b4590b2'

def queryDeepSeek(message):
    history=[]
    user_input=message
    history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=history,
            stream=False
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


if __name__ == '__main__':
    # Please install OpenAI SDK first: `pip3 install openai`
    openai.api_base = "https://api.deepseek.com"
    openai.api_key = 'sk-f6a474403f6746ed9542367e4b4590b2'
    history=[]
    user_input="你好"
    history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=history,
            stream=False
    )
    print(response.choices[0].message.content)



