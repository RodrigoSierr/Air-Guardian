import requests

url = "https://api.openaq.org/v3/measurements?country=PE&limit=1"
headers = {
    "X-API-Key": "838ffdc583a96756a299ab910a8bbc6ced0662b3af558b6cc49a209dc902f3af"
}
resp = requests.get(url, headers=headers)
print(resp.status_code)
print(resp.text)
