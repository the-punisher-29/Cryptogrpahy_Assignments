import socket
from Cryptodome.Cipher import DES3

class DES3Solver:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()
    
    def connect(self):
        """
        Establish a persistent connection to the server and wrap it in a file-like object
        to support line-based I/O. Immediately discard the server’s prompt.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.f = self.sock.makefile("rwb", buffering=0)
        self._discard_prompt()
    
    def _read_line(self):
        """Read one line from the socket and remove its trailing newline."""
        line = self.f.readline()
        if not line:
            raise Exception("Connection closed by server.")
        return line.decode().rstrip("\n")
    
    def _read_prompt(self):
        """Read all lines of the server prompt (assumed to be four lines)."""
        for _ in range(4):
            self._read_line()
    
    def _discard_prompt(self):
        """Read and discard the server prompt."""
        self._read_prompt()
    
    def _send_line(self, line):
        """Send a line to the server and flush the output."""
        self.f.write((line + "\n").encode())
        self.f.flush()
    
    def get_challenge(self):
        """
        Fetch the encrypted challenge from the server using API option 1.
        """
        self._send_line("1")
        challenge_hex = self._read_line().strip()
        self._read_prompt()  # Discard the prompt
        return bytes.fromhex(challenge_hex)
    
    def decrypt(self, ciphertext):
        """
        Use the decryption oracle (API option 2) to decrypt a given ciphertext.
        """
        self._send_line("2")
        self._read_line()  # Discard the ciphertext prompt
        self._send_line(ciphertext.hex())
        decrypted_hex = self._read_line().strip()
        self._read_prompt()  # Discard the prompt
        return bytes.fromhex(decrypted_hex)
    
    def reveal_string(self, plaintext):
        """
        Reveal the content of string.txt using API option 3.
        """
        self._send_line("3")
        self._read_line()  # Read and discard plaintext prompt
        self._send_line(plaintext.hex())
        return self._read_line()
    
    def recover_plaintext(self):
        """
        Recover the original plaintext challenge by analyzing bit flips.
        """
        encrypted_challenge = self.get_challenge()
        flipped_bits = set()
        observed_outputs = []

        print("[*] Starting decryption queries...")
        
        for _ in range(128):
            try:
                decrypted_block = self.decrypt(encrypted_challenge[:8])
            except Exception as e:
                print(f"[!] Error during decryption: {e}")
                break
            
            if observed_outputs:
                previous_output = observed_outputs[-1]
                diff = bytes(a ^ b for a, b in zip(previous_output, decrypted_block))
                for byte_index, byte in enumerate(diff):
                    for bit_index in range(8):
                        if (byte >> bit_index) & 1:
                            flipped_bits.add(byte_index * 8 + bit_index)
            
            observed_outputs.append(decrypted_block)
        
        print(f"[*] Identified flipped bits: {flipped_bits}")
        
        reconstructed_key = bytearray(24)
        for bit_position in flipped_bits:
            byte_index, bit_index = divmod(bit_position, 8)
            reconstructed_key[byte_index] ^= (1 << bit_index)
        
        print(f"[*] Reconstructed key: {reconstructed_key.hex()}")
        cipher = DES3.new(bytes(reconstructed_key), mode=DES3.MODE_CBC, iv=self.iv)
        return cipher.decrypt(encrypted_challenge)
    
    def solve(self):
        """
        Recover the secret challenge and use it to retrieve string.txt.
        """
        try:
            plaintext_challenge = self.recover_plaintext()
            result = self.reveal_string(plaintext_challenge)
            print("Recovered string.txt content:", result)
        finally:
            self.f.close()
            self.sock.close()

if __name__ == "__main__":
    solver = DES3Solver("127.0.0.1", 29103)
    solver.solve()
