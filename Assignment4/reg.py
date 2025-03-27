def caesar_cipher_decrypt(text, shift):
    decrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            decrypted_text += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            decrypted_text += char
    return decrypted_text

cipher_text = "TPSU TUSJLF DJHBS QBUUFSO"

for shift in range(1, 26):
    decrypted = " ".join([caesar_cipher_decrypt(word, shift) for word in cipher_text.split()])
    print(f"Shift {shift}: {decrypted}")
