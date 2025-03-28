#!/usr/bin/env python3
import itertools
import json
import socket
from hashlib import sha512

HOST = "socket.cryptohack.org"
PORT = 13393

# Re‑implementation of the cipher and hash from h11s.py

class MyCipher:
    __NR = 31
    __SB = [13, 14, 0, 1, 5, 10, 7, 6, 11, 3, 9, 12, 15, 8, 2, 4]
    __SR = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]

    def __init__(self, key):
        self.__RK = int(key.hex(), 16)
        self.__subkeys = [
            [ (self.__RK >> (16 * j + i)) & 1 for i in range(16) ]
            for j in range(self.__NR + 1)
        ]

    def __xorAll(self, v):
        res = 0
        for x in v:
            res ^= x
        return res

    def encrypt(self, plaintext):
        assert len(plaintext) == 8, "Plaintext must be 64 bits."
        S = [int(ch, 16) for ch in list(plaintext.hex())]
        for r in range(self.__NR):
            # Add subkey
            S = [S[i] ^ self.__subkeys[r][i] for i in range(16)]
            # Substitution layer
            S = [self.__SB[ S[self.__SR[i]] ] for i in range(16)]
            # Compute XOR in 4-nibble blocks
            X = []
            for i in range(0, 16, 4):
                t = 0
                for x in S[i:i+4]:
                    t ^= x
                X.append(t)
            # Mixing: note the use of two loop variables from product(range(4), range(4))
            S = [X[c] ^ S[4 * c + r_] for c, r_ in itertools.product(range(4), range(4))]
        S = [S[i] ^ self.__subkeys[self.__NR][i] for i in range(16)]
        return bytes.fromhex("".join("{:x}".format(x) for x in S))

class MyHash:
    def __init__(self, content):
        self.cipher = MyCipher(sha512(content).digest())
        self.h = b"\x00" * 8
        self._update(content)

    def _update(self, content):
        # pad content so its length is a multiple of 8 bytes
        while len(content) % 8 != 0:
            content += b"\x00"
        for i in range(0, len(content), 8):
            block = content[i:i+8]
            # xor the block into the current hash
            self.h = bytes([a ^ b for a, b in zip(self.h, block)])
            self.h = self.cipher.encrypt(self.h)
            self.h = bytes([a ^ b for a, b in zip(self.h, block)])
    def digest(self):
        return self.h
    def hexdigest(self):
        return self.h.hex()

def find_fixed_point():
    print("Searching for a fixed point candidate (i.e. x such that MyHash(x)==0)...")
    # Try simple candidates: 8 bytes with the same nibble (16 hex digits)
    for d in "0123456789abcdef":
        candidate = bytes.fromhex(d * 16)  # 16 hex digits → 8 bytes
        h = MyHash(candidate).digest()
        if h == b"\x00" * 8:
            print("Found candidate:", candidate.hex())
            return candidate
    return None

def get_flag(candidate):
    payload = {"option": "hash", "data": candidate.hex()}
    s = socket.create_connection((HOST, PORT))
    s.sendall((json.dumps(payload) + "\n").encode())
    resp = s.recv(1024)
    s.close()
    print("Server response:")
    print(resp.decode())

if __name__ == "__main__":
    candidate = find_fixed_point()
    if candidate is None:
        print("No fixed point found among simple candidates.")
    else:
        get_flag(candidate)