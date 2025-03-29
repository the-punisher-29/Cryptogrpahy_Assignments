import itertools
from collections import Counter
# Convert hex encoded string to bytes
def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)
# Guess key length using frequency analysis.
# For each candidate key length, the ciphertext is split 
# into “blocks” corresponding to each key byte. Then, the frequency 
# of the most common byte is measured. When the correct key length 
# is used, the blocks tend to have a higher frequency for common characters (e.g., space).
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
    # sort by score from highest to lowest
    return sorted(key_length_scores, key=key_length_scores.get, reverse=True)
# Recover the key from the ciphertext. For each byte position in the key,
# find the most common byte within the corresponding coset and XOR it with 32 (ASCII for space).
def recover_key(ciphertext_bytes, key_length):
    key = []
    for i in range(key_length):
        block = ciphertext_bytes[i::key_length]
        freqs = Counter(block)
        most_common_byte, _ = freqs.most_common(1)[0]
        key_byte = most_common_byte ^ 32  # XOR with space (32)
        key.append(key_byte)
    return bytes(key)
# Decrypt the ciphertext using the recovered key. Since XOR is its own inverse,
# we simply XOR each ciphertext byte with the corresponding key byte.
def decrypt(ciphertext_bytes, key):
    plaintext = bytearray()
    for i in range(len(ciphertext_bytes)):
        plaintext.append(ciphertext_bytes[i] ^ key[i % len(key)])
    return plaintext.decode(errors='ignore')

# ---------------------------- Main Section ----------------------------
# Load the ciphertext from file (ciphertext is in hex format)
with open('ciphertext_72.txt', 'r') as file:
    ciphertext_hex = file.read().strip()

# Convert the hex encoded ciphertext to bytes
ciphertext_bytes = hex_to_bytes(ciphertext_hex)

# Step 1: Guess the most likely key lengths from 1 to 40
# The candidate with the highest score is assumed to be the ideal length.
key_lengths = guess_key_length(ciphertext_bytes)
print("Top 5 candidate key lengths:", key_lengths[:5])

# Select ideal key length (here we pick the first candidate from the sorted list)
ideal_key_length = key_lengths[2]
print("Chosen key length:", ideal_key_length)

# Step 2: Recover the encryption key using the chosen key length
key = recover_key(ciphertext_bytes, ideal_key_length)
print("Recovered Key:", key)

# Step 3: Decrypt the entire ciphertext using the recovered key
plaintext = decrypt(ciphertext_bytes, key)
print("Decrypted Plaintext:\n", plaintext)

# Step 4: Extract the random string 
# (assuming that the last 25 characters of the plaintext are the appended random string)
random_string = plaintext[-25:]
print("Extracted Random String:", random_string)
