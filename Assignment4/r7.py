from sympy import factorint

n = 510143758735509025530880200653196460532653147

# Factor n into its prime factors
factors = factorint(n)
print("Factors:", factors)

# Since n factors into two primes, extract the smaller:
smaller_prime = min(factors.keys())
print("The smaller prime is:")
print(smaller_prime)