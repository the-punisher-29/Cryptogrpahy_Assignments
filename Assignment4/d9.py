from pwn import *
from Crypto.Cipher import AES
import hashlib
import json

s=remote('socket.cryptohack.org', '13373')

#decryption from DH starter 5 challenge

def decrypt_flag(shared_secret: int, iv: str, ciphertext: str):
    # Derive AES key from shared secret
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    # Decrypt flag
    ciphertext = bytes.fromhex(ciphertext)
    iv = bytes.fromhex(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

alice=s.recvline().decode()
alice=eval(alice[24:])

p=int(alice["p"],16)
g=int(alice["g"],16)
A=int(alice["A"],16)

# Finding a value
a = A * pow(g, -1, p)

bob=s.recvline().decode()
bob=eval(bob[22:])
B=int(bob["B"],16)
shared_secret = (a * B) % p
print(f"shared_secret:{shared_secret}")

aes_value=s.recvline().decode()
aes_value=eval(aes_value[24:])
print(aes_value)
iv=aes_value["iv"]
ciphertext=aes_value["encrypted"]

shared_secret = 781375771286523921682177536065612640494056443200091700967335945135067268298653748996108322420480852844610393628365669516985078401109539826459162980506903623821748901865082257455849415791691881709448350504513673033914283456716068601658189110168981077531264035904750408276794096099693262398008324260587814780721089721047526118391598923434827194939854735798577674170203256314333942485760352085036751905369610326318228197468392759214066509014997981777945415195218141
iv = "c396c71ca5eef7b2b03f359e30de5924"
ciphertext = "5fcf13b8d7e15aed2ac21bbe0ab732e9e75b221a4cba4c90cd63a25d0dda2461d24bc10e7dceffc0fe5a9b4ae00bfaa7"

print(decrypt_flag(shared_secret, iv, ciphertext))
