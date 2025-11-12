import requests
import json

Baseurl = "https://www.chataiapi.com"  # ✅ 不要带 /v1
Skey = "sk-i9V9UPL3RLOS43zeSgVFxR4V2vwRpoceRLkbIXgkf6sU7rvi"  # 你的 key

payload = {
    "model": "gemini-2.5-pro",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "hello"}
    ]
}

url = f"{Baseurl}/v1/chat/completions"  # ✅ 正确路径
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {Skey}',
    'User-Agent': 'PythonTest/1.0',
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.status_code)
print(response.text)
