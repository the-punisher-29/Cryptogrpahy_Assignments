import socket
from Cryptodome.Cipher import DES3

class DES3Solver:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()
        self.key = b'\x00' * 24
        self.iv = b'\x00' * 8 

    def connect(self):
        """
        Establish a persistent connection to the server and wrap it in a file-like object
        for easier line-based I/O. Immediately discard the initial prompt (which consists
        of four lines).
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        # Use a file wrapper for convenient readline() calls.
        self.f = self.sock.makefile("rwb", buffering=0)
        self._discard_prompt()

    def _read_line(self):
        """
        Read one line from the socket and strip the trailing newline.
        Raises an Exception if the connection is closed.
        """
        line = self.f.readline()
        if not line:
            raise Exception("Connection closed by server.")
        return line.decode().rstrip("\n")

    def _read_prompt(self):
        """
        Read all lines of a prompt. This implementation assumes the prompt consists of exactly
        four lines. Adjust the number if the prompt changes on the server side.
        """
        prompt_lines = []
        for _ in range(4):
            prompt_lines.append(self._read_line())
        return prompt_lines

    def _discard_prompt(self):
        """
        Read and discard the prompt lines (typically four) sent by the server.
        """
        self._read_prompt()

    def _send_line(self, line):
        """
        Write a line to the server (appending a newline character) and flush immediately.
        """
        self.f.write((line + "\n").encode())
        self.f.flush()

    def get_challenge(self):
        """
        Use Option 1 to fetch the encrypted challenge.
        Conversation Protocol:
          - Send "1" to request the challenge.
          - The server responds with a line of hexadecimal string (the encrypted challenge).
          - The server then sends the prompt (four lines) again.
        """
        # Send option "1" to fetch the challenge.
        self._send_line("1")
        # Read the single line holding the hex-encoded challenge.
        challenge_hex = self._read_line().strip()
        try:
            challenge_bytes = bytes.fromhex(challenge_hex)
        except ValueError as e:
            raise ValueError(f"Error converting challenge '{challenge_hex}' to bytes: {e}")
        # Discard the prompt sent after the response.
        self._read_prompt()
        return challenge_bytes

    def decrypt(self, ciphertext):
        """
        Use Option 2 (decryption oracle) to decrypt a given ciphertext.
        Conversation Protocol:
          - Send "2" to start decryption.
          - The server sends a prompt line "(hex) ct:".
          - Send the ciphertext as a hex string.
          - The server replies with a line that is the decrypted text (also as hex).
          - The server sends the full prompt (four lines) again.
        """
        self._send_line("2")
        # Read the prompt for ciphertext (e.g., "(hex) ct:").
        ct_prompt = self._read_line()
        # Send the ciphertext in hex format.
        self._send_line(ciphertext.hex())
        # Read the decrypted hex response.
        decrypted_hex = self._read_line().strip()
        try:
            decrypted_bytes = bytes.fromhex(decrypted_hex)
        except ValueError as e:
            raise ValueError(f"Error converting decrypted text '{decrypted_hex}' to bytes: {e}")
        # Discard the prompt.
        self._read_prompt()
        return decrypted_bytes

    def reveal_string(self, plaintext):
        """
        Use Option 3 to reveal string.txt.
        Conversation Protocol:
          - Send "3" to request the flag.
          - The server sends a prompt for plaintext: "(hex) pt:".
          - Send the challenge plaintext as a hex string.
          - The server replies with the content of string.txt or an error message.
        """
        self._send_line("3")
        # Read the plaintext prompt.
        pt_prompt = self._read_line()
        self._send_line(plaintext.hex())
        # Read the result (either the flag or an error message).
        result = self._read_line()
        return result

    # Move this function inside the class
    def recover_plaintext(self):
        """
        Recover the original plaintext challenge by exploiting deterministic key alteration
        and using the decryption oracle.
        """
        # Step 1: Fetch encrypted challenge
        encrypted_challenge = self.get_challenge()
        
        # Step 2: Exploit deterministic key alteration
        # We will track how the key is altered across multiple decrypt calls.
        # Start with an empty set to track flipped bits.
        flipped_bits = set()
        
        # Decrypt a block of ciphertext repeatedly to observe changes in output.
        observed_plaintexts = []
        for _ in range(24):  # Perform 24 queries (one for each byte of the key)
            decrypted_block = self.decrypt(encrypted_challenge[:8])  # Decrypt only the first block
            observed_plaintexts.append(decrypted_block)
        
        # Analyze changes in decrypted blocks to deduce flipped bits
        # Compare consecutive decrypted outputs to identify which bits were flipped.
        for i in range(1, len(observed_plaintexts)):
            diff = bytes(a ^ b for a, b in zip(observed_plaintexts[i - 1], observed_plaintexts[i]))
            for bit_position in range(8 * len(diff)):  # Check each bit position
                if (diff[bit_position // 8] >> (7 - (bit_position % 8))) & 1:
                    flipped_bits.add(bit_position)
        
        # Step 3: Reverse-engineer original key
        # The original key can be reconstructed by reversing all tracked flips.
        reconstructed_key = bytes(
            b ^ (1 << (7 - (i % 8))) if i in flipped_bits else b
            for i, b in enumerate(self.key)
        )
        
        # Step 4: Decrypt encrypted challenge using reconstructed key
        cipher = DES3.new(reconstructed_key, mode=DES3.MODE_CBC, iv=self.iv)
        recovered_plaintext = cipher.decrypt(encrypted_challenge)
        
        return recovered_plaintext

    # Move this function inside the class
    def solve(self):
        """
        Recover the secret challenge (by exploiting the decryption oracle) and then reveal string.txt.
        """
        try:
            # Recover the plaintext challenge.
            plaintext_challenge = self.recover_plaintext()
            
            # Submit the recovered plaintext and print the result.
            result = self.reveal_string(plaintext_challenge)
            print("Recovered string.txt content:", result)
        
        finally:
            self.f.close()
            self.sock.close()

if __name__ == "__main__":
    solver = DES3Solver("127.0.0.1", 29103)
    solver.solve()
