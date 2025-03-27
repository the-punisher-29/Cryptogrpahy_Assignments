import math

# Total number of possible outputs (11 bits)
hash_space = 2 ** 11  # 2048

def collision_probability(n, space):
    # Calculate the probability that n secrets have no collision
    prob_no_collision = 1.0
    for i in range(n):
        prob_no_collision *= (space - i) / space
    return 1 - prob_no_collision

n = 0
while True:
    n += 1
    p = collision_probability(n, hash_space)
    if p >= 0.75:
        print(f"Approximately {n} unique secrets give a collision probability of {p*100:.2f}%")
        break