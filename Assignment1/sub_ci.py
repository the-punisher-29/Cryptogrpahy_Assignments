def create_mapping():
    return {
        'R': ' ',    # Space - verified
        'k': '.',    # Period - verified
        'S': ',',    # Comma - needs update
        'E': 't',    # Common letter - verified
        'W': 'n',    # Common letter - verified
        '+': 'h',    # Common letter - verified
        'y': 'i',    # Common letter - verified
        '<': 'e',    # Common letter - verified
        'u': 'd',    # Common letter - verified
        '~': 'a',    # Common letter - verified
        '/': 'o',    # Common letter - verified
        'w': 's',    # Common letter - verified
        'Q': 'g',    # Letter - verified
        'O': 'y',    # Letter - verified
        'C': 'u',    # Letter - verified
        'F': 'C',    # Capital letter - updated
        'B': 'h',    # Letter - verified
        'H': 'R',    # Capital letter - verified
        '1': 'M',    # Capital letter - verified
        'A': 'A',    # Capital letter - updated
        'm': 'p',    # Letter - verified
        'G': 'v',    # Letter - verified
        'U': 'b',    # Letter - verified
        'J': 'T',    # Capital letter - verified
        '.': 'c',    # Letter - verified
        'L': 'P',    # Capital letter - verified
        'V': 'x',    # Letter - verified
        'N': 'B',    # Capital letter - verified
        'I': 'I',    # Capital letter - verified
        'M': 'j',    # Letter - verified
        'P': 'w',    # Letter - verified
        'Y': 'z',    # Letter - verified
        'X': 'q',    # Letter - verified
        'Z': 'W',    # Capital letter - verified
        'D': 'G',    # Capital letter - verified
        '{': '[',    # Symbol - verified
        '}': ']',    # Symbol - verified
        '_': '(',    # Symbol - verified
        'n': ')',    # Symbol - verified
        '-': '/',    # Symbol - verified
        '=': '=',    # Symbol - verified
        "'": "'",    # Symbol - verified
        ',': '.',    # Symbol - updated
        '.': ',',    # Symbol - updated
        '!': '1',    # Number - verified
        '@': '3',    # Number - verified
        '#': '4',    # Number - verified
        '$': '9',    # Number - verified
        '%': '0',    # Number - verified
        'T': '7',    # Number - verified
        'e': '8',    # Number - verified
        'g': '2',    # Number - verified
        'x': '6',    # Number - verified
        '*': 'k',    # Letter - verified
        '`': '`',    # Symbol - verified
    }

def find_random_string(cipher_text):
    """Find the random string at the beginning of the cipher text."""
    lines = cipher_text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('R'):  # If line is not empty and doesn't start with space
            return line
    return None

def decrypt_text(cipher_text, mapping):
    """Decrypt the cipher text using the provided mapping."""
    decrypted_text = ''
    for char in cipher_text:
        if char in mapping:
            decrypted_text += mapping[char]
        else:
            decrypted_text += char  # Keep unmapped characters as is
    return decrypted_text

def main():
    # Read the cipher text from file
    try:
        with open('ciphertext_test_72.txt', 'r') as f:
            cipher_text = f.read()
    except FileNotFoundError:
        print("Please create a file named 'cipher.txt' with your cipher text")
        return

    # Create mapping
    mapping = create_mapping()
    
    # Find random string
    random_string = find_random_string(cipher_text)
    print("Random String Found:", random_string)
    print("\nDecrypted Random String:", decrypt_text(random_string, mapping))
    
    # Decrypt entire text
    decrypted_text = decrypt_text(cipher_text, mapping)
    
    # Save decrypted text to file
    with open('decrypted.txt', 'w') as f:
        f.write(decrypted_text)
    
    print("\nFull text has been decrypted and saved to 'decrypted.txt'")

if __name__ == "__main__":
    main()