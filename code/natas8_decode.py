import base64, json, urllib.parse


# $encodedSecret = "3d3d516343746d4d6d6c315669563362";

# function encodeSecret($secret) {
#    return bin2hex(strrev(base64_encode($secret)));
# }


startSecret = '3d3d516343746d4d6d6c315669563362'

def decodeSecret(startSecret):
    secret = bytes.fromhex(startSecret).decode('utf-8')
    secret = secret[::-1]
    secret = base64.b64decode(secret)

    return secret

print(decodeSecret(startSecret=startSecret))

default_data = '{"showpassword":"no","bgcolor":"#ffffff"}'
enc_cookie = 'EGAgHwQ1IxYYMSQYGSZxTUksPFVHYDEQCC0%2FGBlgaVVIJDURDSQ1VRY%3D'
clean_enc_cookie = urllib.parse.unquote(enc_cookie)

xor_cipher = base64.b64decode(clean_enc_cookie).decode('latin-1')

leaked_key_chars = []
def xorDecrypt(text, key):
    for i in range(len(text)):
        key_char = chr(ord(text[i]) ^ ord(key[i]))
        leaked_key_chars.append(key_char)

xorDecrypt(default_data, xor_cipher)

full_string = "".join(leaked_key_chars)
print(f'Repeating key string: {full_string}')

def findKey(full_key_string):
    key_length = 1
    while True:
        print(f"Current key length: {key_length}")
        key = full_key_string[:key_length]
        print(f"Trying key: {key}")
        repeat_times = ( len(full_key_string) // key_length ) + 1
        reconstructed =  key * repeat_times

        if reconstructed.startswith(full_key_string):
            print(f"Found key : {key}")
            return key
        
        if (key_length > len(full_key_string)):
            print("Failed to find key ... aborting")
            break

        key_length += 1

key = findKey(full_string)
payload = '{"showpassword":"yes","bgcolor":"#800080"}'

def xorPayload(payload, key):
    enc_cookie = []
    for i in range(len(payload)):
        enc_cookie_char = chr(ord(payload[i]) ^ ord(key[i % len(key)]))
        enc_cookie.append(enc_cookie_char)
    return "".join(enc_cookie)

raw_encrypted = xorPayload(payload=payload, key=key)
b64_encode = base64.b64encode(raw_encrypted.encode('latin-1')).decode('utf-8')
cookie_value = urllib.parse.quote(b64_encode)

print(cookie_value)