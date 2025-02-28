import socket
import subprocess
import re
import os

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5000        # Change this as needed

whitelist = {
    "date": None,
    "echo": "[\\w. ]+",
    "ls": "[/\\w]+",
}

whiteset = set(cmd.encode() for cmd in whitelist)

def helper(cmd, data):
    if cmd == "encrypt":
        data = [ord(c) for c in data]
    else:
        data = list(bytes.fromhex(data))

    while len(data) < 16:
        data.append(0)

    inp = cmd + " " + " ".join("%02x" % c for c in data[:16])
    
    try:
        res = subprocess.check_output("./aes", input=inp.encode())
        return bytes.fromhex(res.decode())
    except subprocess.CalledProcessError:
        return b"Error: Could not process command"

def process_command(command):
    try:
        what, rest = command.split(" ", 1)
    except ValueError:
        return b"Invalid command format."
    
    if what == "encrypt":
        cmd = rest.split(" ")[0]
        if cmd not in whitelist:
            return f"I won't encrypt that. ('{cmd}' not in whitelist)".encode()
        
        regex = [cmd]
        if whitelist[cmd]:
            regex.append(whitelist[cmd])
        regex = " ".join(regex)
        
        if not re.fullmatch(regex, rest):
            return f"I won't encrypt that. ('{rest}' does not match '{regex}')".encode()
        
        res = helper("encrypt", rest)
        return b"Encrypted command: " + res.hex().encode()
    
    elif what == "run":
        command = helper("decrypt", rest).rstrip(b"\x00")
        cmd = command.split(b" ")[0]
        
        if cmd not in whiteset:
            return f"I won't run that. ({cmd} not in whitelist)".encode()
        
        res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        return b"Output: " + res.stdout
    
    else:
        return b"Invalid command."

# Start the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}...")
    
    while True:
        conn, addr = server.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break
                
                print(f"Received command: {data}")
                response = process_command(data)
                conn.sendall(response)