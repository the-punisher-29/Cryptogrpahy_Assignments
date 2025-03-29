import re
import subprocess
import os
import socket

HOST = "0.0.0.0"
PORT = 5000

def menu(conn):
    conn.sendall(b"What do you want to do?\n")
    conn.sendall(b"- encrypt command (e.g. 'encrypt echo test')\n")
    conn.sendall(b"- run command (e.g. 'run fefed6ce5359d0e886090575b2f1e0c7')\n")
    conn.sendall(b"- exit\n")

def helper(cmd, data):
    if cmd == "encrypt":
        data = [ord(c) for c in data]
    else:
        data = list(bytes.fromhex(data))
    
    while len(data) < 16:
        data.append(0)
    
    inp = cmd + " " + " ".join("%02x" % c for c in data[:16])
    res = subprocess.check_output("./aes", input=inp.encode())
    return bytes.fromhex(res.decode())

def handle_client(conn):
    conn.sendall(b"Welcome to encrypted command runner.\n")
    whitelist = {
        "date": None,
        "echo": "[\\w. ]+",
        "ls": "[/\\w]+",
    }
    whiteset = set(cmd.encode() for cmd in whitelist)
    counter = 0
    
    while True:
        counter += 1
        if counter > 100:
            conn.sendall(b"All right, I think that's enough for now.\n")
            break
        
        menu(conn)
        line = conn.recv(1024).decode().strip()
        if not line:
            continue
        
        if line == "exit":
            conn.sendall(b"Bye.\n")
            break
        
        parts = line.split(" ", 1)
        if len(parts) != 2:
            conn.sendall(b"Invalid input.\n")
            continue
        
        what, rest = parts
        
        if what == "encrypt":
            cmd = rest.split(" ", 1)[0]
            if cmd not in whitelist:
                conn.sendall(f"I won't encrypt that. ('{cmd}' not in whitelist)\n".encode())
                continue
            regex = [cmd]
            if whitelist[cmd]:
                regex.append(whitelist[cmd])
            regex = " ".join(regex)
            if not re.fullmatch(regex, rest):
                conn.sendall(f"I won't encrypt that. ('{rest}' does not match '{regex}')\n".encode())
                continue
            res = helper("encrypt", rest)
            conn.sendall(f"Encrypted command: {res.hex()}\n".encode())
        elif what == "run":
            command = helper("decrypt", rest).rstrip(b"\x00")
            cmd = command.split(b" ")[0]
            if cmd not in whiteset:
                conn.sendall(f"I won't run that. ({cmd.decode()} not in whitelist)\n".encode())
                continue
            res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            conn.sendall(b"Output: " + res.stdout + b"\n")
        else:
            conn.sendall(b"What?\n")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = server.accept()
            print(f"Connection from {addr}")
            handle_client(conn)
            conn.close()
            print(f"Connection closed for {addr}")

if __name__ == "__main__":
    main()
