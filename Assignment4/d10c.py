#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/solve.py
import socket, json, hashlib, sys
from Crypto.Cipher import AES
from binascii import unhexlify

def pkcs7_unpad(data):
    padding_len = data[-1]
    if padding_len < 1 or padding_len > AES.block_size:
        raise ValueError("Bad padding")
    if data[-padding_len:] != bytes([padding_len])*padding_len:
        raise ValueError("Bad padding")
    return data[:-padding_len]

HOST = "socket.cryptohack.org"
PORT = 13378

# Connect to server.
s = socket.create_connection((HOST, PORT))
f = s.makefile("rw")

# Step 1. Receive parameters from Bob's partner.
# Expected JSON: {"p": "<p>", "g": "<g>", "A": "<A>"}.
line = f.readline()
if not line:
    print("No data received")
    sys.exit(1)
params = json.loads(line)
# We ignore the provided g.
print("[*] Received parameters:")
print("p =", params["p"])
print("g =", params["g"])
print("Partner A =", params["A"])

# Step 2. Send our malicious public key.
# We set our public key B = 1.
malicious = {"B": "1"}
f.write(json.dumps(malicious) + "\n")
f.flush()
print("[*] Sent malicious public key B = 1")

# Step 3. Receive the encrypted message.
line = f.readline()
if not line:
    print("No response received")
    sys.exit(1)
resp = json.loads(line)
ct_hex = resp["ct"]
iv_hex = resp["iv"]
print("[*] Received ciphertext and iv")
print("ct =", ct_hex)
print("iv =", iv_hex)

# Step 4. Since we forced g = 1, the shared secret is 1.
# Derive the AES key as sha1(b"1") and take first 16 bytes.
shared = b"1"
key = hashlib.sha1(shared).digest()[:16]

# Decrypt the ciphertext using AES-CBC.
ct = unhexlify(ct_hex)
iv = unhexlify(iv_hex)
cipher = AES.new(key, AES.MODE_CBC, iv)
pt = cipher.decrypt(ct)
flag = pkcs7_unpad(pt).decode()
print("[*] Flag:", flag)

s.close()