import openai

# server_ip = '172.17.62.88'
server_ip = '115.190.109.233'
url = f'http://{server_ip}:20005'
model = 'zhipu-api'

if __name__ == "__main__":
    openai.api_base = f'http://{server_ip}:20005/v1'
    openai.api_key = "none"
    history = []
    while True:
        user_input = input("用户：")
        history.append({"role": "user", "content": user_input})
        if user_input.lower() == "exit":
            break
        response = openai.ChatCompletion.create(
            # model="chatglm3-6b",
            model=model,
            messages=history,
            stream=False
        )
        if response.choices[0].message.role == "assistant":
            print(model + ': ', response.choices[0].message.content)
            history.append({"role": "assistant", "content": response.choices[0].message.content})