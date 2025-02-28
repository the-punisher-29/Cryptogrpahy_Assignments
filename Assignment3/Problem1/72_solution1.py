import socket
import binascii

# Configuration: use the correct HOST and PORT where your server is running
HOST = "127.0.0.1"
PORT = 12345

def recv_until(sock, delimiter, timeout=2):
    """Receive data until the delimiter text is found."""
    sock.settimeout(timeout)
    data = b""
    while delimiter.encode() not in data:
        try:
            chunk = sock.recv(1024)
        except socket.timeout:
            break
        if not chunk:
            break
        data += chunk
    return data.decode()

def main():
    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        
        # Receive the welcome message and prompt from the server
        welcome = recv_until(sock, "Choose an API option")
        print("Server Welcome Message:")
        print(welcome)
        
        # Step 1: Fetch the encrypted challenge (Option 1)
        sock.sendall(b"1\n")
        response = recv_until(sock, "Choose an API option")
        # Assume the first line is the hex-encoded challenge ciphertext.
        challenge_ciphertext_hex = response.splitlines()[0].strip()
        print("Encrypted Challenge (hex):", challenge_ciphertext_hex)
        
        # Step 2: Decrypt the challenge (Option 2)
        sock.sendall(b"2\n")
        # Wait for the prompt "(hex) ct: " and send the ciphertext.
        prompt = recv_until(sock, "(hex) ct:")
        print("Server prompt for decryption:", prompt)
        sock.sendall((challenge_ciphertext_hex + "\n").encode())
        decryption_response = recv_until(sock, "Choose an API option")
        # The first line should contain the hex text of the decrypted challenge.
        decrypted_challenge_hex = decryption_response.splitlines()[0].strip()
        print("Decrypted Challenge (hex):", decrypted_challenge_hex)
        
        # Step 3: Reveal the secret string (Option 3)
        sock.sendall(b"3\n")
        prompt = recv_until(sock, "(hex) pt:")
        print("Server prompt for secret reveal:", prompt)
        sock.sendall((decrypted_challenge_hex + "\n").encode())
        final_response = recv_until(sock, "\n")
        print("Secret string response:")
        print(final_response)

if __name__ == "__main__":
    main()
