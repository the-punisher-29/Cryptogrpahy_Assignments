from collections import Counter

def index_of_coincidence(segment):
    """
    Compute IoC for a sequence (segment) of bytes.
    IoC = (sum over all letters of f*(f-1)) / (N*(N-1))
    """
    N = len(segment)
    if N < 2:
        return 0.0
    freqs = Counter(segment)
    numerator = sum(freq * (freq - 1) for freq in freqs.values())
    denominator = N * (N - 1)
    return numerator / denominator

def guess_key_length(cipher_bytes, max_key_length=40):
    """
    For each candidate key length from 1 to max_key_length,
    split the ciphertext into that many cosets (taking every nth
    byte) and compute the average IoC value over all cosets.
    The candidate with a higher IoC (typically above ~0.06 for English)
    is more likely to be the correct key length.
    Returns a dictionary mapping key length to avg IoC.
    """
    results = {}
    for key_length in range(1, max_key_length + 1):
        iocs = []
        # Split the ciphertext into key_length blocks (cosets)
        for i in range(key_length):
            coset = cipher_bytes[i::key_length]
            iocs.append(index_of_coincidence(coset))
        avg_ioc = sum(iocs) / len(iocs)
        results[key_length] = avg_ioc
    return results

# Example usage:
# Load your ciphertext from a file (assuming it is in hexadecimal format)
with open('ciphertext_14.txt', 'r') as file:
    ciphertext_hex = file.read().strip()

# Convert hex to bytes
cipher_bytes = bytes.fromhex(ciphertext_hex)

# Run the key length guesser over candidate lengths from 1 to 40
ioc_dict = guess_key_length(cipher_bytes, max_key_length=40)

# Display candidate key lengths and their average IoC values
# (A candidate with an IoC closer to the English IoC ~0.0667 is preferred)
print("Key Length Candidate : Avg IoC")
for key_length in sorted(ioc_dict):
    print(f"{key_length:>3} : {ioc_dict[key_length]:.4f}")

# One may then select the key length with the highest average IoC.
best_candidate = max(ioc_dict, key=lambda k: ioc_dict[k])
print("\nBest (most likely) key length candidate:", best_candidate)
