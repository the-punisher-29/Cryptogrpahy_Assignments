import signal
import os
import random
import sys
from Cryptodome.Cipher import DES3
import socket
import threading

class Functional_Des:
    def __init__(self):
        self.key = os.urandom(24)
        self.iv = os.urandom(8)
        self.flipped_bits = set(range(0, 192, 8))
        self.challenge = os.urandom(64)
        self.counter = 128

    def get_random_string(self, plain):
        if plain == self.challenge:
            with open("string.txt", "rb") as f:
                FLAG = f.read()
            return FLAG
        raise Exception("Not quite right")

    def get_challenge(self):
        cipher = DES3.new(self.key, mode=DES3.MODE_CBC, iv=self.iv)
        return cipher.encrypt(self.challenge)

    def alter_key(self):
        if len(self.flipped_bits) == 192:
            self.flipped_bits = set(range(0, 192, 8))
        remaining = list(set(range(192)) - self.flipped_bits)
        num_flips = random.randint(1, len(remaining))
        self.flipped_bits = self.flipped_bits.union(
            random.choices(remaining, k=num_flips))
        mask = int.to_bytes(sum(2**i for i in self.flipped_bits), 24, byteorder="big")
        return bytes(i ^ j for i, j in zip(self.key, mask))

    def decrypt(self, text: bytes):
        self.counter -= 1
        if self.counter < 0:
            raise Exception("Out of balance")
        key = self.alter_key()
        if len(text) % 8 != 0:
            return b''
        cipher = DES3.new(key, mode=DES3.MODE_CBC, iv=self.iv)
        return cipher.decrypt(text)
    
PROMPT = (
    "Choose an API option\n"
    "1. Fetch challenge\n"
    "2. Decrypt\n"
    "3. Reveal Random String\n"
)

def handle_client(client_socket, chall):
    try:
        client_socket.sendall(PROMPT.encode())
        while True:
            # Read the option from the client.
            data = client_socket.recv(1024)
            if not data:
                break
            try:
                option = int(data.decode().strip())
            except Exception:
                client_socket.sendall("Invalid option\n".encode())
                continue

            if option == 1:
                # Option 1: Fetch encrypted challenge.
                challenge_enc = chall.get_challenge().hex()
                client_socket.sendall((challenge_enc + "\n").encode())
            elif option == 2:
                # Option 2: Decrypt a given ciphertext.
                client_socket.sendall("(hex) ct: ".encode())
                ct_data = client_socket.recv(4096)
                if not ct_data:
                    break
                try:
                    ct = bytes.fromhex(ct_data.decode().strip())
                except Exception:
                    client_socket.sendall("Invalid hex input\n".encode())
                    continue
                try:
                    decrypted = chall.decrypt(ct).hex()
                    client_socket.sendall((decrypted + "\n").encode())
                except Exception as e:
                    client_socket.sendall((str(e) + "\n").encode())
                    break
            elif option == 3:
                # Option 3: Reveal the random string if the submitted plaintext matches.
                client_socket.sendall("(hex) pt: ".encode())
                pt_data = client_socket.recv(4096)
                if not pt_data:
                    break
                try:
                    pt = bytes.fromhex(pt_data.decode().strip())
                except Exception:
                    client_socket.sendall("Invalid hex input\n".encode())
                    continue
                try:
                    result = chall.get_random_string(pt)
                    client_socket.sendall(result + b"\n")
                except Exception as e:
                    client_socket.sendall((str(e) + "\n").encode())
                # After Option 3 the session exits.
                break
            else:
                client_socket.sendall("Invalid option\n".encode())

            # Re-send the prompt for further actions.
            client_socket.sendall(PROMPT.encode())
    except Exception as e:
        try:
            client_socket.sendall((str(e) + "\n").encode())
        except Exception:
            pass
    finally:
        client_socket.close()

def start_server(host="127.0.0.1", port=29103):
    """
    This function sets up the server. It creates an instance
    of Functional_Des and listens for incoming connections.
    Each client gets its own thread.
    """
    # Set a global timeout for the process (128 seconds)
    signal.alarm(128)
    chall = Functional_Des()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")
    
    try:
        while True:
            client_socket, addr = server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            # Create a new thread to handle the client.
            client_handler = threading.Thread(target=handle_client, args=(client_socket, chall))
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    # chall = Functional_Des()
    # PROMPT = ("Choose an API option\n"
    #           "1. Fetch challenge\n"
    #           "2. Decrypt\n"
    #           "3. Reveal Random String\n")
    # signal.alarm(128)
    # while True:
    #     try:
    #         option = int(input(PROMPT))
    #         if option == 1:
    #             print(chall.get_challenge().hex())
    #         elif option == 2:
    #             ct = bytes.fromhex(input("(hex) ct: "))
    #             print(chall.decrypt(ct).hex())
    #         elif option == 3:
    #             pt = bytes.fromhex(input("(hex) pt: "))
    #             print(chall.get_random_string(pt))
    #             sys.exit(0)
    #     except Exception as e:
    #         print(e)
    #         sys.exit(1)
    start_server()
