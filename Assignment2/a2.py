import itertools
from collections import Counter
# Function to convert hex to bytes
def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)
# Function to guess key length using frequency analysis
def guess_key_length(ciphertext_bytes, max_key_length=40):
    key_length_scores = {}
    for key_len in range(1, max_key_length + 1):
        blocks = [ciphertext_bytes[i::key_len] for i in range(key_len)]
        score = 0
        for block in blocks:
            freqs = Counter(block)
            most_common_byte, count = freqs.most_common(1)[0]
            score += count / len(block)
        key_length_scores[key_len] = score / key_len
    return sorted(key_length_scores, key=key_length_scores.get, reverse=True)
# Function to recover the key using XOR analysis
def recover_key(ciphertext_bytes, key_length):
    key = []
    for i in range(key_length):
        block = ciphertext_bytes[i::key_length]
        freqs = Counter(block)
        most_common_byte, _ = freqs.most_common(1)[0]
        # Assuming space (ASCII 32) is the most frequent character in plaintext
        key_byte = most_common_byte ^ 32
        key.append(key_byte)
    return bytes(key)
# Function to decrypt ciphertext using the recovered key
def decrypt(ciphertext_bytes, key):
    plaintext = bytearray()
    for i in range(len(ciphertext_bytes)):
        plaintext.append(ciphertext_bytes[i] ^ key[i % len(key)])
    return plaintext.decode(errors='ignore')
# Load ciphertext from file (replace 'ciphertext_72.txt' with your file path)
with open('ciphertext_72.txt', 'r') as file:
    ciphertext_hex = file.read().strip()
# Convert hex to bytes
ciphertext_bytes = hex_to_bytes(ciphertext_hex)
# Step 1: Guess the most likely key lengths
key_lengths = guess_key_length(ciphertext_bytes)
print("Most likely key lengths:", key_lengths[:5])
# Step 2: Recover the encryption key (assuming the first guessed length is correct)
key_length = key_lengths[0]
key = recover_key(ciphertext_bytes, key_length)
print("Recovered Key:", key)
# # Step 3: Decrypt the ciphertext and extract plaintext
plaintext = decrypt(ciphertext_bytes, key)
print("Decrypted Plaintext:", plaintext)
# Step 4: Extract the random string (assuming it's the last 25 characters of plaintext)
random_string = plaintext[-25:]
print("Random String:", random_string)
