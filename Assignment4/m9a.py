from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Known ciphertext and key
ciphertext = bytes.fromhex('fef29e5ff72f28160027959474fc462e2a9e0b2d84b1508f7bd0e270bc98fac942e1402aa12db6e6a36fb380e7b53323')
key = b'\x00' * 32  # Replace with actual key if known

# Initialize AES cipher in ECB mode
cipher = AES.new(key, AES.MODE_ECB)

# Attempt to decrypt block by block
block_size = 16
blocks = [ciphertext[i:i + block_size] for i in range(0, len(ciphertext), block_size)]

flag = b''
for block in blocks:
    try:
        decrypted_block = cipher.decrypt(block)
        flag += decrypted_block
    except Exception as e:
        print(f"Error decrypting block: {e}")

print(f"Recovered Flag: {flag.decode('utf-8')}")
