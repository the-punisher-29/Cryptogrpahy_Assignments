#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/solve.py
import sys, math
from Crypto.Util.number import long_to_bytes, inverse

# Increase recursion limit for potential deep calculations
sys.setrecursionlimit(10**7)

# Given output parameters
n = 709872443186761582125747585668724501268558458558798673014673483766300964836479167241315660053878650421761726639872089885502004902487471946410918420927682586362111137364814638033425428214041019139158018673749256694555341525164012369589067354955298579131735466795918522816127398340465761406719060284098094643289390016311668316687808837563589124091867773655044913003668590954899705366787080923717270827184222673706856184434629431186284270269532605221507485774898673802583974291853116198037970076073697225047098901414637433392658500670740996008799860530032515716031449787089371403485205810795880416920642186451022374989891611943906891139047764042051071647203057520104267427832746020858026150611650447823314079076243582616371718150121483335889885277291312834083234087660399534665835291621232056473843224515909023120834377664505788329527517932160909013410933312572810208043849529655209420055180680775718614088521014772491776654380478948591063486615023605584483338460667397264724871221133652955371027085804223956104532604113969119716485142424996255737376464834315527822566017923598626634438066724763559943441023574575168924010274261376863202598353430010875182947485101076308406061724505065886990350185188453776162319552566614214624361251463
e = 65537
c = 608484617316138126443275660524263025508135383745665175433229598517433030003704261658172582370543758277685547533834085899541036156595489206369279739210904154716464595657421948607569920498815631503197235702333017824993576326860166652845334617579798536442066184953550975487031721085105757667800838172225947001224495126390587950346822978519677673568121595427827980195332464747031577431925937314209391433407684845797171187006586455012364702160988147108989822392986966689057906884691499234298351003666019957528738094330389775054485731448274595330322976886875528525229337512909952391041280006426003300720547721072725168500104651961970292771382390647751450445892361311332074663895375544959193148114635476827855327421812307562742481487812965210406231507524830889375419045542057858679609265389869332331811218601440373121797461318931976890674336807528107115423915152709265237590358348348716543683900084640921475797266390455366908727400038393697480363793285799860812451995497444221674390372255599514578194487523882038234487872223540513004734039135243849551315065297737535112525440094171393039622992561519170849962891645196111307537341194621689797282496281302297026025131743423205544193536699103338587843100187637572006174858230467771942700918388

# From the prime generation code:
# p = (D * s^2 + 1) // 4 where D = 427
D = 427

def isqrt(n):
    """Integer square root"""
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

def direct_factor_attempt():
    """Direct factorization using the expected range of s"""
    print("[*] Attempting direct factorization...")
    
    # We know s is in range 2^1020 to 2^1021-1 from challenge code
    # To avoid overflow when working with floats, we'll estimate s differently
    
    # Get a rough bit size for sqrt(n)
    n_bit_length = n.bit_length()
    s_bit_estimate = n_bit_length // 4  # Roughly 1024 bits for s
    
    # Create a reasonable range for s near 2^1020
    s_start = 2**1020
    
    # Try several values around this estimate
    # We'll try increments in a reasonable range
    increment = 2**1010  # A reasonable step size
    iterations = 1000    # Limit our search
    
    for i in range(iterations):
        s = s_start + i * increment
        p_candidate = (D * s**2 + 1) // 4
        
        # Check if this is a factor of n
        if n % p_candidate == 0:
            q_candidate = n // p_candidate
            return p_candidate, q_candidate
            
        # Also try a slightly smaller s
        s = s_start - i * increment
        if s > 0:  # Ensure s is positive
            p_candidate = (D * s**2 + 1) // 4
            if n % p_candidate == 0:
                q_candidate = n // p_candidate
                return p_candidate, q_candidate
    
    return None, None

def fermat_factorization():
    """Fermat's factorization method, which works well when factors are close"""
    print("[*] Attempting Fermat's factorization method...")
    
    # s is around 2^1020, so p ≈ D*(2^1020)²/4 ≈ D*(2^2040)/4
    # q is about 2048 bits, so roughly 2^2048
    # This means p and q are not too far apart, which is good for Fermat's method
    
    a = isqrt(n) + 1
    max_iterations = 10000
    
    for i in range(max_iterations):
        b2 = a*a - n
        b = isqrt(b2)
        
        if b*b == b2:  # Perfect square, we found factors
            p = a + b
            q = a - b
            return p, q
        
        a += 1
    
    return None, None

def special_factor():
    """Use the special structure: p = (D*s² + 1)/4 where s is near 2^1020"""
    print("[*] Attempting factorization using the special prime structure...")
    
    # Since s is roughly 2^1020, we can try values in that range
    s_base = 2**1020
    
    # Try variations around this base value
    for offset in range(-1000, 1000):
        s = s_base + offset
        p_candidate = (D * s**2 + 1) // 4
        
        # Check if this is a valid factor
        if n % p_candidate == 0:
            q_candidate = n // p_candidate
            return p_candidate, q_candidate
    
    # Try another approach: search for s where s² is close to 4*sqrt(n)/D
    # Since 4p = D*s² + 1, we have s² ≈ 4p/D ≈ 4*sqrt(n)/D
    s_approx = isqrt((4 * isqrt(n)) // D)
    
    # Search around this approximation
    for offset in range(-1000, 1000):
        s = s_approx + offset
        p_candidate = (D * s**2 + 1) // 4
        
        # Check if this is a valid factor
        if n % p_candidate == 0:
            q_candidate = n // p_candidate
            return p_candidate, q_candidate
            
    return None, None

def main():
    print("[*] Attempting to factor n using multiple approaches...")
    
    # Try our direct method first
    p, q = direct_factor_attempt()
    
    if p is None:
        # Try special factorization based on p's structure
        p, q = special_factor()
    
    if p is None:
        # Try Fermat's factorization method
        p, q = fermat_factorization()
    
    if p is not None and q is not None:
        print("[+] Successfully factored n!")
        print(f"p = {p}")
        print(f"q = {q}")
        
        # Calculate d = e^(-1) mod phi(n)
        phi = (p-1)*(q-1)
        d = inverse(e, phi)
        
        # Decrypt the message
        m = pow(c, d, n)
        flag = long_to_bytes(m)
        print(f"[+] Found flag: {flag.decode()}")
        return flag
    else:
        print("[-] Failed to factor n using the attempted methods")
        return None

if __name__ == "__main__":
    main()