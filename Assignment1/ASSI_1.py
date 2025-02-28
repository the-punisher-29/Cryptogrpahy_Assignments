from collections import Counter

def find_key_length(ciphertext):
    """
    Uses Kasiski examination or index of coincidence to estimate key length.
    """
    def calculate_ic(text):
        """Calculate Index of Coincidence (IC) for a given text."""
        n = len(text)
        frequencies = Counter(text)
        ic = sum(f * (f - 1) for f in frequencies.values()) / (n * (n - 1))
        return ic
    
    # Test different key lengths and find IC close to English text (~0.068)
    likely_lengths = []
    for key_len in range(1, 21):  # Test key lengths up to 20
        segments = [ciphertext[i::key_len] for i in range(key_len)]
        avg_ic = sum(calculate_ic(segment) for segment in segments) / key_len
        likely_lengths.append((key_len, avg_ic))
    
    # Return the most likely key length based on IC
    likely_lengths.sort(key=lambda x: abs(x[1] - 0.068))
    return likely_lengths[0][0]

def find_vigenere_key(ciphertext, key_length):
    """
    Finds the Vigenère cipher key using frequency analysis.
    """
    def shift_char(c, shift):
        """Shift character by given amount."""
        return chr(((ord(c) - ord('A') - shift) % 26) + ord('A'))
    
    key = ''
    for i in range(key_length):
        segment = ciphertext[i::key_length]
        frequencies = Counter(segment)
        most_common_char = frequencies.most_common(1)[0][0]
        # Assume 'E' is the most frequent letter in English
        shift = (ord(most_common_char) - ord('E')) % 26  
        key += shift_char('A', shift)
    
    return key

def decrypt_vigenere(ciphertext, key):
    """
    Decrypts a Vigenère cipher given a ciphertext and a key.
    """
    decrypted_text = []
    key_length = len(key)
    
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            shift = ord(key[i % key_length]) - ord('A')
            new_char = chr(((ord(char.upper()) - ord('A') - shift) % 26) + ord('A'))
            # Preserve original casing
            decrypted_text.append(new_char.lower() if char.islower() else new_char)
        else:
            decrypted_text.append(char)
    
    return ''.join(decrypted_text)


filename = "v_ciphertext_72.txt"
with open(filename, "r") as file:
    ciphertext_vigenere = file.read().strip()

# Use the functions defined above to determine the key and decrypt the message:
key_length = find_key_length(ciphertext_vigenere)
key = find_vigenere_key(ciphertext_vigenere, key_length)
plaintext_vigenere = decrypt_vigenere(ciphertext_vigenere, key)

print("Key Length:", key_length)
print("Key:", key)
print("Decrypted Plaintext:", plaintext_vigenere)
