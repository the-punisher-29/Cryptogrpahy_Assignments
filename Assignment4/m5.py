from math import gcd

# Given sequence of successive powers modulo p
seq = [588,665,216,113,642,4,836,114,851,492,819,237]

# Function to find prime p by checking gcd of differences
def find_prime(seq):
    diffs = []
    for i in range(len(seq)-1):
        diff = seq[i]**2 - seq[i-1]*seq[i+1]
        diffs.append(diff)
    
    from math import gcd
    from functools import reduce
    
    # Compute gcd of all diffs to find prime p
    p = abs(diffs[0])
    for d in diffs[1:]:
        p = gcd(p:=abs(diff), abs(diffs[0]))
        if p > 1:
            return p
    return None

# Simple gcd function
def gcd(a,b):
    while b:
        a,b=b,a%b
    return a

# Find prime modulus p
p = None
for i in range(1,len(seq)-1):
    candidate = abs(seq[i]**2 - seq[i-1]*seq[i+1])
    if candidate == 0:
        continue
    if not p:
        p = candidate
    else:
        p = gcd(p,candidate)

# Confirm prime modulus found is a three-digit prime
print(f"Prime modulus found: {p}")

# Now find integer x using modular inverse (x ≡ next * inv(prev) mod p)
def modinv(a,m):
    g,x,y=extended_gcd(a,m)
    if g!=1:
        raise Exception('No modular inverse')
    else:
        return x%m

def extended_gcd(a,b):
    if a==0:
        return b,0,1
    else:
        g,x1,y1=extended_gcd(b%a,a)
        x=y1-(b//a)*x1
        y=x1
        return g,x,y

# Compute x using first two terms: x ≡ seq[1]*inv(seq[0]) mod p
x = (seq[1]*modinv(seq[0],p))%p

print(f"The prime modulus (p) is: {p}")
print(f"The integer (x) is: {x}")
print(f"The flag is: crypto{{{p},{x}}}")
