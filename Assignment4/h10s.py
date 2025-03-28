#!/usr/bin/env python3
import socket
import json

HOST = "socket.cryptohack.org"
PORT = 13402

# You can try sending a controlled query.
# For example, here we send hex "00"*len(FLAG) (if FLAG were 32 bytes, for instance)
# But since the mixing process uses a random mask and then a one‐way hash,
# no matter what input you send you will only get the sha256 digest of masked data.
# Thus you cannot recover the FLAG.
test_data = "00" * 31  # adjust length if known

payload = {
    "option": "mix",
    "data": test_data
}

s = socket.create_connection((HOST, PORT))
s.sendall((json.dumps(payload) + "\n").encode())
resp = s.recv(1024)
s.close()

print("Response:")
print(resp.decode())