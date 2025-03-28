#!/usr/bin/env python3
import json
import socket
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

HOST = "socket.cryptohack.org"
PORT = 13378

# Malicious Diffie–Hellman parameters.
p = 37       # Use a prime accepted by Bob
g = 1
A = 1

payload = {"p": p, "g": g, "A": A}

s = socket.create_connection((HOST, PORT))
s.sendall((json.dumps(payload) + "\n").encode())

# Read the full response.
resp = b""
while True:
    part = s.recv(4096)
    if not part:
        break
    resp += part
s.close()

print("Raw response:", resp)

# Split the raw response by lines.
raw_lines = resp.decode().splitlines()

# Initialize dictionaries.
bob_data = None
alice_data = None

# Process each line and extract JSON from the ones we need.
for line in raw_lines:
    if line.startswith("Intercepted from Bob:"):
        try:
            json_text = line.split("Intercepted from Bob:", 1)[1].strip()
            bob_data = json.loads(json_text)
        except Exception as e:
            print("Error parsing Bob's data:", e)
    elif line.startswith("Intercepted from Alice:"):
        try:
            json_text = line.split("Intercepted from Alice:", 1)[1].strip()
            data_candidate = json.loads(json_text)
            if "iv" in data_candidate:
                alice_data = data_candidate
        except Exception as e:
            print("Error parsing Alice's data:", e)

if not bob_data or not alice_data:
    print("Failed to extract necessary JSON data.")
    exit(1)

print("Bob's data:", bob_data)
print("Alice's data:", alice_data)

# Get iv and the encrypted ciphertext.
iv = bytes.fromhex(alice_data["iv"])
ct = bytes.fromhex(alice_data["encrypted"])  # note key is "encrypted"

# Since g is 1, the shared secret is always 1.
shared_secret = 1

# Derive the AES key.
key = hashlib.sha1(str(shared_secret).encode()).digest()[:16]

# Decrypt using AES-CBC.
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(ct)

# Try to unpad (if PKCS#7 padding was used); if not, fall back to stripping null bytes.
try:
    plaintext = unpad(decrypted, AES.block_size)
except ValueError:
    plaintext = decrypted.rstrip(b"\x00")

print("Enter flag here:", plaintext.decode())