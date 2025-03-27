#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/solve.py
import socket
from binascii import hexlify, unhexlify

BLOCK_SIZE = 32

# Constants from h4s.py
W = [0x6b17d1f2, 0xe12c4247, 0xf8bce6e5, 0x63a440f2,
     0x77037d81, 0x2deb33a0, 0xf4a13945, 0xd898c296]
X = [0x4fe342e2, 0xfe1a7f9b, 0x8ee7eb4a, 0x7c0f9e16,
     0x2bce3357, 0x6b315ece, 0xcbb64068, 0x37bf51f5]
Y = [0xc97445f4, 0x5cdef9f0, 0xd3e05e1e, 0x585fc297,
     0x235b82b5, 0xbe8ff3ef, 0xca67c598, 0x52018192]
Z = [0xb28ef557, 0xba31dfcb, 0xdd21ac46, 0xe2a91e3c,
     0x304f44cb, 0x87058ada, 0x2cb81515, 0x1e610046]

def to_bytes(arr):
    return b"".join(x.to_bytes(4, 'big') for x in arr)

W_bytes = to_bytes(W)
X_bytes = to_bytes(X)
Y_bytes = to_bytes(Y)
Z_bytes = to_bytes(Z)

# Basic helper functions
def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def rotate_left(data, r):
    r %= BLOCK_SIZE
    return data[r:] + data[:r]

def rotate_right(data, r):
    r %= BLOCK_SIZE
    return data[-r:] + data[:-r]

# scramble_block applies 40 rounds of a fixed linear round function.
def scramble_block(block):
    for _ in range(40):
        block = xor(W_bytes, block)
        block = rotate_left(block, 6)
        block = xor(X_bytes, block)
        block = rotate_right(block, 17)
    return block

# Inverse of one round of scramble_block.
def scramble_round_inv(block):
    # invert the round:
    # round: b -> b1 = xor(W_bytes, b)
    #         b2 = rotate_left(b1,6)
    #         b3 = xor(X_bytes, b2)
    #         b4 = rotate_right(b3,17)
    # Invert by reversing steps:
    b3 = rotate_left(block, 17)            # invert rotate_right by rotate_left
    b2 = xor(b3, X_bytes)                 # invert xor with X_bytes
    b1 = rotate_right(b2, 6)               # invert rotate_left by rotate_right
    b  = xor(b1, W_bytes)                 # invert xor with W_bytes
    return b

# Inverse of scramble_block (40 rounds)
def unscramble_block(block):
    for _ in range(40):
        block = scramble_round_inv(block)
    return block

# For block 1, extra mixing is performed:
def F(b):
    # For block index i=1, after scramble_block we do one iteration:
    #   mix = scramble_block(b)
    #   mix = rotate_right(mix, i+11) => i=1 so 12
    #   mix = xor(mix, X_bytes)
    #   mix = rotate_left(mix, i+6) => 7
    mix = scramble_block(b)
    mix = rotate_right(mix, 12)
    mix = xor(mix, X_bytes)
    mix = rotate_left(mix, 7)
    return mix

# For a one–block message, the update is:
#   H(m) = I XOR scramble_block(m)
# where I = xor(Y_bytes,Z_bytes)
def H_one(block):
    I = xor(Y_bytes, Z_bytes)
    return xor(I, scramble_block(block))

# For a two–block message [b0 || b1], update is:
#   H(m) = I XOR (scramble_block(b0) XOR F(b1))
def H_two(b0, b1):
    I = xor(Y_bytes, Z_bytes)
    return xor(I, xor(scramble_block(b0), F(b1)))

# We now build a collision.
# Choose b0 and b1 arbitrarily (here 32 zero bytes)
b0 = bytes([0]*BLOCK_SIZE)
b1 = bytes([0]*BLOCK_SIZE)

# Compute intermediate values:
r0 = scramble_block(b0)  # T0(b0)
F_b1 = F(b1)           # F(b1)
# Our target for a one–block collision message is:
target = xor(r0, F_b1)

# Invert scramble_block to get bA such that scramble_block(bA) = target.
bA = unscramble_block(target)

# Check: collision: H_one(bA) == H_two(b0,b1)
if H_one(bA) != H_two(b0, b1):
    raise Exception("Collision construction failed!")
    
print("[*] Collision constructed!")
print("Message A (one block):", hexlify(bA).decode())
print("Message B (two blocks):", hexlify(b0+b1).decode())

# Now, connect to the challenge server.
HOST = "socket.cryptohack.org"
PORT = 13405

def recvall(s):
    data = b""
    while True:
        part = s.recv(4096)
        if not part:
            break
        data += part
        if b"\n" in part:
            break
    return data

print("[*] Connecting to server at {}:{}...".format(HOST, PORT))
s = socket.create_connection((HOST, PORT))
f = s.makefile("rw")

# Receive initial banner / prompt (adjust reading as needed)
banner = f.readline().strip()
print("[*] Banner:", banner)

# Depending on the protocol the server may ask you to submit a collision.
# For example, it might prompt:
# "Enter two messages that collision under our hash (hex encoded):"
# Adjust the protocol interaction as needed.

# Here we send our two messages (hex encoded) separated by newlines.
f.write(hexlify(bA).decode() + "\n")
f.write(hexlify(b0+b1).decode() + "\n")
f.flush()

# Read and print server response.
response = f.read()
print("[*] Server response:\n", response)

s.close()