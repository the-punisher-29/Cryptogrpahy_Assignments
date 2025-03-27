import socket
import json
from sympy import randprime

HOST = "socket.cryptohack.org"
PORT = 13385

# Generate a valid prime p (600-900 bits)
p = randprime(2**600, 2**900)

flag = ""

# Try increasing `a` values to maximize x
for a in range(2, 1000):  
    data = json.dumps({"prime": p, "base": a})
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Server:", s.recv(1024).decode())  # Read welcome message
        
        s.sendall(data.encode() + b"\n")  # Send prime and base
        response = s.recv(1024).decode()  # Get response
        
        if "Success" in response:
            flag_part = response.split(": ")[-1].strip()
            print(f"Recovered Flag Part: {flag_part}")

            # If more characters are revealed, update flag
            if len(flag_part) > len(flag):
                flag = flag_part
            
            # Stop when full flag is revealed
            if "}" in flag:
                print(f"Full Flag: {flag}")
                break
