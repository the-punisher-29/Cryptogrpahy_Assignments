import math

def solve_RSA_challenge(N, e1, e2, c1, c2):
    # Calculating the difference between the two expressions to obtain a multiple of q
    diff = (pow(c1, e2, N) * pow(5, e1 * e2, N) - pow(c2, e1, N) * pow(2, e1 * e2, N)) % N

    # Computing q using the gcd approach
    q = math.gcd(diff, N)
    p = N // q

    return p, q

# Lecture des données à partir de data.txt
with open('m7d.txt', 'r') as f:
    N = int(f.readline().strip())
    e1 = int(f.readline().strip())
    e2 = int(f.readline().strip())
    c1 = int(f.readline().strip())
    c2 = int(f.readline().strip())

# Solve the challenge
p, q = solve_RSA_challenge(N, e1, e2, c1, c2)

print("p:", p)
print("q:", q)