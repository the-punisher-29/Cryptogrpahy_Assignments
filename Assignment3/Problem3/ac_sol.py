from pwn import *
from Crypto.Cipher import AES
import subprocess

# Connect to the server at 0.0.0.0:5000
r = remote("0.0.0.0", 5000)

r.recvuntil(b"run command (e.g. 'run ")

encrypted_echo = bytes.fromhex(r.recvline().split(b"'")[0].decode())

r.sendline(("encrypt ls " + "ą" * 13).encode())
r.recvuntil(b"Encrypted command: ")
line = r.recvline().strip()
r.sendline(b"run " + line)
r.recvuntil(b"Output: ls: cannot access ")
line = r.recvuntil(b": No such file or directory").rsplit(b":", 1)[0]

# Parse bash string
cmd = b"echo -n " + line
out = subprocess.check_output(["bash", "-c", cmd])

key = [0, 0, 0] + [0x52 ^ o for o in out]

found = False
for a in range(76, 256):
    if found:
        break
    key[0] = a
    for b in range(256):
        if found:
            break
        key[1] = b
        for c in range(256):
            key[2] = c
            cipher = AES.new(bytes(key), AES.MODE_ECB)
            pt = cipher.decrypt(encrypted_echo)
            if pt.startswith(b'echo'):
                print("plaintext", pt)
                found = True
                break

print("full key", bytes(key))

cmd = b"echo ;cat /flag"
cmd += b"\x00" * (16 - len(cmd))
cipher = AES.new(bytes(key), AES.MODE_ECB)
ct = cipher.encrypt(cmd).hex()

r.sendline(b"run " + ct.encode())
r.recvuntil(b"Output:")
out = r.recvuntil(b"What do")
flag = out.splitlines()[1].decode()

r.sendline(b"exit")
r.recvall()

print("Flag:", flag)

assert flag.startswith("CTF{")
