import socket
import time
from collections import Counter

class DES3Solver:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()
    
    def connect(self):
        """
        Establish a persistent connection to the server and wrap it for line-based I/O.
        Immediately discard the initial multi-line prompt (assumed to be four lines).
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.f = self.sock.makefile("rwb", buffering=0)
        self._discard_prompt()
    
    def _read_line(self):
        """
        Read one line from the socket (without its trailing newline).
        Raise an exception if nothing is returned.
        """
        line = self.f.readline()
        if not line:
            raise Exception("Connection closed by server.")
        return line.decode().rstrip("\n")
    
    def _read_prompt(self):
        """
        Read the prompt sent by the server.
        (Assumes the prompt is exactly four lines; adjust if needed.)
        """
        prompt_lines = []
        for _ in range(4):
            prompt_lines.append(self._read_line())
        return prompt_lines
    
    def _discard_prompt(self):
        """Discard the prompt sent by the server."""
        self._read_prompt()
    
    def _send_line(self, line):
        """Send a line (with newline appended) to the server and flush."""
        self.f.write((line + "\n").encode())
        self.f.flush()
    
    def get_challenge(self):
        """
        API Option 1:
         - Send "1" to fetch the encrypted challenge.
         - Read one line containing the ciphertext (hex encoded).
         - Discard the subsequent prompt (four lines).
        """
        self._send_line("1")
        challenge_hex = self._read_line().strip()
        try:
            challenge_bytes = bytes.fromhex(challenge_hex)
        except Exception as e:
            raise Exception(f"Error converting challenge '{challenge_hex}' to bytes: {e}")
        self._read_prompt()  # discard trailing prompt
        return challenge_bytes
    
    def decrypt(self, ciphertext):
        """
        API Option 2:
         - Send "2" to start decryption.
         - Read the prompt (for example, "(hex) ct:").
         - Send the provided ciphertext as a hexadecimal string.
         - Read one line containing the decrypted output (hex encoded).
         - Discard the following prompt.
        """
        self._send_line("2")
        self._read_line()  # read and ignore the ciphertext prompt.
        self._send_line(ciphertext.hex())
        decrypted_hex = self._read_line().strip()
        try:
            decrypted_bytes = bytes.fromhex(decrypted_hex)
        except Exception as e:
            raise Exception(f"Error converting decrypted text '{decrypted_hex}' to bytes: {e}")
        self._read_prompt()  # discard trailing prompt.
        return decrypted_bytes
    
    def reveal_string(self, plaintext):
        """
        API Option 3:
         - Send "3" to reveal string.txt.
         - Read the prompt for plaintext (e.g. "(hex) pt:").
         - Send the candidate plaintext as a hex string.
         - Read and return the server's response (the flag or an error message).
        """
        self._send_line("3")
        self._read_line()  # discard plaintext prompt.
        self._send_line(plaintext.hex())
        result = self._read_line()
        return result
    
    def recover_plaintext_statistical(self):
        """
        Original statistical approach:
          1. Fetch the encrypted challenge.
          2. Make multiple decryption oracle queries (up to 128).
          3. Track frequencies of each candidate plaintext.
          4. Return the most frequent candidate or one that reaches a threshold.
        """
        encrypted_challenge = self.get_challenge()
        candidate_counts = {}
        candidate_outputs = {}
        max_queries = 128
        threshold = 3
        
        print("[*] Starting statistical recovery (backup method)...")
        
        for i in range(max_queries):
            try:
                candidate = self.decrypt(encrypted_challenge)
            except Exception as e:
                print(f"[!] Error during decryption query {i+1}: {e}")
                # Reconnect if connection closed
                try:
                    self.f.close()
                    self.sock.close()
                except Exception:
                    pass
                time.sleep(1)
                self.connect()
                encrypted_challenge = self.get_challenge()
                candidate = self.decrypt(encrypted_challenge)
            
            cand_hex = candidate.hex()
            candidate_counts[cand_hex] = candidate_counts.get(cand_hex, 0) + 1
            candidate_outputs[cand_hex] = candidate
            
            print(f"Query {i+1}: Candidate = {cand_hex}, Frequency = {candidate_counts[cand_hex]}")
            
            if candidate_counts[cand_hex] >= threshold:
                print(f"[*] Candidate {cand_hex} reached frequency {candidate_counts[cand_hex]}; selecting it.")
                return candidate
        
        # If no candidate reached the threshold, choose the most frequent one
        best_candidate_hex = max(candidate_counts, key=candidate_counts.get)
        print(f"[*] Selecting candidate {best_candidate_hex} (frequency: {candidate_counts[best_candidate_hex]}).")
        return candidate_outputs[best_candidate_hex]
    
    def analyze_bit_differences(self, previous, current):
        """
        Analyze which bits changed between two decryption outputs.
        Returns a list of (byte_index, bit_index) tuples for each flipped bit.
        """
        flipped_bits = []
        for byte_idx in range(min(len(previous), len(current))):
            # XOR the bytes to get a byte where each 1 bit indicates a difference
            diff_byte = previous[byte_idx] ^ current[byte_idx]
            for bit_idx in range(8):
                if (diff_byte >> bit_idx) & 1:
                    flipped_bits.append((byte_idx, bit_idx))
        return flipped_bits
    
    def recover_plaintext_optimal(self):
        """
        Optimized method to recover the original plaintext when the decryption oracle 
        uses keys with random bit flips.
        
        This approach:
        1. Gets the encrypted challenge
        2. Makes multiple decryption queries while analyzing bit patterns
        3. Identifies stable output regions
        4. Uses both consecutive matches and statistical analysis
        5. Implements early termination when confidence is high
        """
        encrypted_challenge = self.get_challenge()
        print(f"[*] Encrypted challenge: {encrypted_challenge.hex()}")
        
        # Track all observed outputs
        observations = []
        
        # Variables for tracking consecutive matches
        last_result = None
        consecutive_same = 0
        streak_threshold = 3
        
        # Track bit flip statistics across all outputs
        bit_flip_history = []
        
        # Track candidate frequencies
        candidate_counter = Counter()
        
        # For each block, track how stable each bit position is
        block_size = 8  # DES block size
        num_blocks = (len(encrypted_challenge) + block_size - 1) // block_size
        
        # Track bit stability across all observations (higher = more stable)
        bit_stability = [[0 for _ in range(8)] for _ in range(len(encrypted_challenge))]
        
        print("[*] Starting optimized key recovery (max 128 queries)...")
        max_queries = 128
        
        for query in range(max_queries):
            try:
                # Get current decryption with potentially flipped key bits
                current_decryption = self.decrypt(encrypted_challenge)
                current_hex = current_decryption.hex()
                
                # Update frequency counter
                candidate_counter[current_hex] += 1
                
                # Check for stability (consecutive identical results)
                if current_hex == last_result:
                    consecutive_same += 1
                    if consecutive_same >= streak_threshold - 1:
                        print(f"[+] Found stable output after {query+1} queries with {consecutive_same+1} consecutive matches")
                        return current_decryption
                else:
                    consecutive_same = 0
                
                # Add to observations
                observations.append(current_decryption)
                
                # After we have at least two observations, analyze bit differences
                if len(observations) >= 2:
                    flipped_bits = self.analyze_bit_differences(observations[-2], observations[-1])
                    bit_flip_history.append(flipped_bits)
                    
                    # Update bit stability counters (increment for bits that didn't flip)
                    for byte_idx in range(len(current_decryption)):
                        for bit_idx in range(8):
                            if (byte_idx, bit_idx) not in flipped_bits:
                                bit_stability[byte_idx][bit_idx] += 1
                
                # Every 8 queries, check if we have sufficient statistical evidence
                if (query + 1) % 8 == 0 and query >= 15:
                    # Calculate block stability scores
                    block_stability = []
                    for block in range(num_blocks):
                        start_byte = block * block_size
                        end_byte = min(start_byte + block_size, len(encrypted_challenge))
                        
                        # Calculate stability score for this block
                        block_score = 0
                        for byte_idx in range(start_byte, end_byte):
                            for bit_idx in range(8):
                                # Normalize stability score by number of comparisons
                                stability = bit_stability[byte_idx][bit_idx] / (len(observations) - 1)
                                block_score += stability
                        
                        # Normalize by total bits in block
                        total_bits = (end_byte - start_byte) * 8
                        block_score /= total_bits
                        block_stability.append(block_score)
                    
                    # Find the most frequent candidate so far
                    most_common = candidate_counter.most_common(1)[0]
                    most_common_hex, frequency = most_common
                    
                    # Calculate confidence based on frequency and stability
                    confidence = frequency / (query + 1)
                    avg_stability = sum(block_stability) / len(block_stability)
                    
                    print(f"[*] Analysis after {query+1} queries:")
                    print(f"    - Most common candidate: {most_common_hex} ({frequency}/{query+1} = {confidence:.2%})")
                    print(f"    - Average block stability: {avg_stability:.2%}")
                    
                    # If we have high confidence and stability, terminate early
                    if confidence >= 0.25 and avg_stability >= 0.7:
                        print(f"[+] Early termination with confidence {confidence:.2%} and stability {avg_stability:.2%}")
                        return bytes.fromhex(most_common_hex)
                
                last_result = current_hex
                
            except Exception as e:
                print(f"[!] Error during query {query+1}: {e}")
                try:
                    self.f.close()
                    self.sock.close()
                except Exception:
                    pass
                time.sleep(1)
                self.connect()
                encrypted_challenge = self.get_challenge()
        
        # If we used all queries, return the most common result
        if candidate_counter:
            most_common_hex, frequency = candidate_counter.most_common(1)[0]
            print(f"[*] Used all {max_queries} queries. Most frequent result: {most_common_hex} ({frequency}/{max_queries})")
            return bytes.fromhex(most_common_hex)
        
        print("[!] Failed to recover plaintext with optimized method. Trying statistical method...")
        return self.recover_plaintext_statistical()
    
    def recover_plaintext(self):
        """
        Main entry point for plaintext recovery.
        Tries the optimized method first, with fallback to statistical method.
        """
        try:
            return self.recover_plaintext_optimal()
        except Exception as e:
            print(f"[!] Optimized recovery failed: {e}")
            print("[*] Falling back to statistical method...")
            return self.recover_plaintext_statistical()
    
    def solve(self):
        """
        Execute the complete attack:
          1. Recover the candidate plaintext
          2. Submit it via API Option 3 to reveal string.txt
          3. Print the result
        """
        try:
            print("[*] Starting 3DES Key Recovery attack...")
            plaintext_challenge = self.recover_plaintext()
            print(f"[+] Recovered plaintext: {plaintext_challenge.hex()}")
            
            print("[*] Submitting recovered plaintext to reveal string.txt...")
            result = self.reveal_string(plaintext_challenge)
            print(f"[+] Success! Recovered string.txt content: {result}")
            return result
        except Exception as e:
            print(f"[!] Attack failed: {e}")
        finally:
            try:
                self.f.close()
                self.sock.close()
            except Exception:
                pass
            print("[*] Connection closed.")

def main():
    host = "127.0.0.1"
    port = 29103
    import sys
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    
    print(f"[*] Connecting to {host}:{port}...")
    solver = DES3Solver(host, port)
    return solver.solve()

if __name__ == "__main__":
    main()