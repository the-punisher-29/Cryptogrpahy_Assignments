from collections import Counter
import itertools

def htob(hex_string):
    return bytes.fromhex(hex_string)

with open('ciphertext_72.txt', 'r') as file:
    ciphertext = file.read()

cipher_text = htob(ciphertext)

# i have the key length and ciphertext..i have to write function to recover the key
def recover_key(cipher_text,key_length):
    key=[]
    for i in range(key_length):
        blk=cipher_text[i::key_length]
        freq=Counter(blk)
        mcb, _ = freq.most_common(1)[0]
        key_byte = mcb ^ 32 #ascii for space
        key.append(key_byte)
    return bytes(key)

key_length = 10
key = recover_key(cipher_text, key_length)
print(key)

str = "0a560f5473"
normalstr = bytes.fromhex(str)
print(normalstr)
decrypted = normalstr ^ key
print(decrypted)














































































import itertools
from collections import Counter
def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

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

def recover_key(ciphertext_bytes, key_length):
    key = []
    for i in range(key_length):
        block = ciphertext_bytes[i::key_length]
        freqs = Counter(block)
        most_common_byte, _ = freqs.most_common(1)[0]
        key_byte = most_common_byte ^ 32  # XOR with space (32)
        key.append(key_byte)
    return bytes(key)

def decrypt(ciphertext_bytes, key):
    plaintext = bytearray()
    for i in range(len(ciphertext_bytes)):
        plaintext.append(ciphertext_bytes[i] ^ key[i % len(key)])
    return plaintext.decode(errors='ignore')


# def index_of_coincidence(segment):
#     N = len(segment)
#     if N < 2:
#         return 0.0
#     freqs = Counter(segment)
#     numerator = sum(freq * (freq - 1) for freq in freqs.values())
#     denominator = N * (N - 1)
#     return numerator / denominator

# def guess_key_length(cipher_bytes, max_key_length=40):
#     results = {}
#     for key_length in range(1, max_key_length + 1):
#         iocs = []
#         for i in range(key_length):
#             coset = cipher_bytes[i::key_length]
#             iocs.append(index_of_coincidence(coset))
#         avg_ioc = sum(iocs) / len(iocs)
#         results[key_length] = avg_ioc
#     return results