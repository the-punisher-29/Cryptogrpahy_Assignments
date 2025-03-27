from pwn import *
import json
s=remote('socket.cryptohack.org','13374')

e_n_value=json.dumps({"option": "get_pubkey",}).encode()
ct=json.dumps({"option": "get_secret",}).encode()

 
print(s.recvline().decode())
s.sendline(ct)

secret=eval(s.recvline().decode())
ciphertext=secret['secret']
flag=json.dumps({"option":"sign","msg":str(ciphertext)}).encode()

s.sendline(flag)
print(s.recvline().decode())

'''
Output: 
TODO: audit signing server to make sure that meddling hacker doesn't 
get hold of my secret 
flag: crypto{d0n7_516n_ju57_4ny7h1n6}
'''
