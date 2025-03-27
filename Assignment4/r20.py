import math
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.number import *
import gmpy2
import binascii

e = 0x10001

p=51894141255108267693828471848483688186015845988173648228318286999011443419469
q=77342270837753916396402614215980760127245056504361515489809293852222206596161
n = p * q
phi = (p - 1) * (q - 1)

d=gmpy2.invert(e,phi)
#Note: don't forget to change the datatype of d from mpz to int
d=int(d)
key = RSA.construct((n, e, d))
cipher = PKCS1_OAEP.new(key)
ct="249d72cd1d287b1a15a3881f2bff5788bc4bf62c789f2df44d88aae805b54c9a94b8944c0ba798f70062b66160fee312b98879f1dd5d17b33095feb3c5830d28"
ct=binascii.unhexlify(ct)
pt = cipher.decrypt(ct)
print("Plaintext: \n",pt)

'''
Plaintext: 
b'crypto{p00R_3570n14}'
'''
