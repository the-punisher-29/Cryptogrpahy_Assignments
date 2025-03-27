#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/m11c_solve.py

import socket
import json
import re

def persistent_connection(host="socket.cryptohack.org", port=13403):
    return socket.create_connection((host, port))

def send_msg(s, msg):
    s.sendall((json.dumps(msg) + "\n").encode())

def recv_msg(s):
    response = b""
    while not response.endswith(b"\n"):
        chunk = s.recv(4096)
        if not chunk:
            break
        response += chunk
    text = response.decode().strip()
    try:
        return json.loads(text)
    except Exception:
        return text

def extract_hex(s):
    """Extract the first hex number from a string."""
    m = re.search(r"0x[0-9a-fA-F]+", s)
    if m:
        return m.group(0)
    raise ValueError("No hex string found in response")

def main():
    s = persistent_connection()
    
    # Step 1: Receive q from the server.
    send_msg(s, {})  # initial empty message to trigger prime generation
    q_resp = recv_msg(s)
    if isinstance(q_resp, dict):
        print("Unexpected JSON response for q:", q_resp)
        s.close()
        return
    try:
        q_hex = extract_hex(q_resp)
    except ValueError as err:
        print("Error extracting q:", err)
        print("Raw q response:", q_resp)
        s.close()
        return
    q = int(q_hex, 16)
    print("Received q:", q)
    
    # Step 2: Send our own parameters.
    # We choose n = q^2 and g = 1 + q so that pow(g, q, n) = 1.
    g = q + 1
    n = q * q
    params_msg = {
        "g": hex(g),
        "n": hex(n)
    }
    send_msg(s, params_msg)
    h_resp = recv_msg(s)
    
    # Debug: print raw h response for inspection.
    print("Raw h response:", h_resp)
    
    if isinstance(h_resp, dict):
        print("Server error on parameters:", h_resp)
        s.close()
        return
    try:
        h_hex = extract_hex(h_resp)
    except ValueError as err:
        print("Error extracting h:", err)
        print("Raw h response:", h_resp)
        s.close()
        return
    print("Received h:", h_hex)
    h = int(h_hex, 16)
    
    # Step 3: Recover the secret x.
    # Since (1+q)^x ≡ 1 + x*q (mod q^2), we have:
    x = (h - 1) // q
    print("Computed private key x:", x)
    
    # Step 4: Send our guess for the server's private key.
    secret_msg = {
        "x": hex(x)
    }
    send_msg(s, secret_msg)
    final_resp = recv_msg(s)
    print("Response:", final_resp)
    s.close()

if __name__ == "__main__":
    main()