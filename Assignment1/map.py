# ...existing code...

def generate_dynamic_mapping(plaintext, ciphertext):
    """Generate additional mappings by aligning plaintext and ciphertext."""
    mapping = create_mapping()  # start with the existing static dict
    pt_index, ct_index = 0, 0
    while pt_index < len(plaintext) and ct_index < len(ciphertext):
        pc, cc = plaintext[pt_index], ciphertext[ct_index]
        if cc not in mapping:
            mapping[cc] = pc
            pt_index += 1
            ct_index += 1
        else:
            if mapping[cc] == pc:
                pt_index += 1
                ct_index += 1
            else:
                ct_index += 1
    return mapping

def main():
    with open("/home/soumen/Dev/crypto/NetworkWorkingGroup.txt", "r") as f:
        known_plaintext = f.read()

    with open("/home/soumen/Dev/crypto/ciphertext_test_72.txt", "r") as f:
        cipher_text = f.read()

    refined_mapping = generate_dynamic_mapping(known_plaintext, cipher_text)
    decrypted = decrypt_text(cipher_text, refined_mapping)
    print(decrypted)

if __name__ == "__main__":
    main()
# ...existing code...