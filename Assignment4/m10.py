#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/m10s_solve.py

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.number import inverse
from hashlib import sha1
from sympy.ntheory.residue_ntheory import discrete_log

# Provided parameters
p = 173754216895752892448109692432341061254596347285717132408796456167143559
D = 529  # =23^2

# Public keys (from m10s.py output)
Ax = 155781055760279718382374741001148850818103179141959728567110540865590463
Ay = 73794785561346677848810778233901832813072697504335306937799336126503714

Bx = 171226959585314864221294077932510094779925634276949970785138593200069419
By = 54353971839516652938533335476115503436865545966356461292708042305317630

# Generator G
Gx = 29394812077144852405795385333766317269085018265469771684226884125940148
Gy = 94108086667844986046802106544375316173742538919949485639896613738390948

# Encrypted flag data
iv_hex = "64bc75c8b38017e1397c46f85d4e332b"
ct_hex = "13e4d200708b786d8f7c3bd2dc5de0201f0d7879192e6603d7c5d6b963e1df2943e3ff75f7fda9c30a92171bbbc5acbf"

iv = bytes.fromhex(iv_hex)
ct  = bytes.fromhex(ct_hex)

# Mapping function: from a point (x, y) we get a field element using:
# psi(P) = x - 23*y  (since sqrt(D)=23)
def psi(x, y):
    return (x - 23 * y) % p

gen = psi(Gx, Gy)
A_phi = psi(Ax, Ay)
B_phi = psi(Bx, By)

print("Computed parameters:")
print("gen   =", gen)
print("A_phi =", A_phi)
print("B_phi =", B_phi)

# Recover Alice's private exponent n_a by solving:
# A_phi = gen^(n_a) mod p
n_a = discrete_log(p, A_phi, gen)
print("Recovered Alice's private exponent n_a:", n_a)

# Compute s = B_phi^(n_a) mod p.
s = pow(B_phi, n_a, p)
# Compute s⁻¹ modulo p.
s_inv = inverse(s, p)
# The shared secret x-coordinate is (s + s_inv) / 2 modulo p.
two_inv = inverse(2, p)
shared_x = ((s + s_inv) % p) * two_inv % p
print("Computed shared secret x-coordinate:", shared_x)

# Derive AES key from shared secret.
key = sha1(str(shared_x).encode('ascii')).digest()[:16]
print("Derived AES key (hex):", key.hex())

# Decrypt the flag.
cipher = AES.new(key, AES.MODE_CBC, iv)
try:
    flag = unpad(cipher.decrypt(ct), 16)
    print("Recovered flag:", flag)
except Exception as e:
    print("Error during decryption:", e)