import socket
import re
import sys

def connect_to_server(host, port):
    """Connect to the remote server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def recv_until(s, pattern):
    """Receive data until a specific pattern is matched."""
    buffer = b""
    while True:
        data = s.recv(1024)
        if not data:
            break
        buffer += data
        if re.search(pattern, buffer.decode(), re.DOTALL):
            break
    return buffer.decode()

def send_command(s, command):
    """Send a command to the server."""
    s.sendall(f"{command}\n".encode())
    return recv_until(s, r"Encrypted command: ([0-9a-f]+)")

def exploit_ecb_mode(s):
    """Exploit the ECB mode weakness to construct a malicious command."""
    # Encrypt two different allowed commands
    response1 = send_command(s, "encrypt ls /secret")
    match1 = re.search(r"Encrypted command: ([0-9a-f]+)", response1)
    if not match1:
        print("[-] Encryption failed for ls /secret")
        return
    encrypted_ls_secret = match1.group(1)
    
    response2 = send_command(s, "encrypt cat /tmp")
    match2 = re.search(r"Encrypted command: ([0-9a-f]+)", response2)
    if not match2:
        print("[-] Encryption failed for cat /tmp")
        return
    encrypted_cat_tmp = match2.group(1)
    
    # Craft a hybrid payload
    hybrid_payload = encrypted_cat_tmp[:32] + encrypted_ls_secret[32:]
    print(f"[+] Crafted hybrid payload: {hybrid_payload}")
    
    send_command(s, f"run {hybrid_payload}")
    response = recv_until(s, r"Output: (.*?)\n")
    print("[+] Exploit result:", response)

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    print(f"[+] Connecting to {host}:{port}")
    s = connect_to_server(host, port)
    
    print("[+] Attempting ECB mode exploit...")
    exploit_ecb_mode(s)
    
    s.close()
    print("[+] Connection closed.")

if __name__ == "__main__":
    main()
