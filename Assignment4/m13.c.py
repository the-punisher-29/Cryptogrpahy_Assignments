#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/solve.py
import socket
import json
from Crypto.Util.number import inverse, long_to_bytes

HOST = "socket.cryptohack.org"
PORT = 13398

# Provided parameters from m13s.py challenge code:
# (N and g as given in the challenge)
N = int("56135841374488684373258694423292882709478511628224823806418810596720294684253418942704418179091997825551647866062286502441190115027708222460662070779175994701788428003909010382045613207284532791741873673703066633119446610400693458529100429608337219231960657953091738271259191554117313396642763210860060639141073846574854063639566514714132858435468712515314075072939175199679898398182825994936320483610198366472677612791756619011108922142762239138617449089169337289850195216113264566855267751924532728815955224322883877527042705441652709430700299472818705784229370198468215837020914928178388248878021890768324401897370624585349884198333555859109919450686780542004499282760223378846810870449633398616669951505955844529109916358388422428604135236531474213891506793466625402941248015834590154103947822771207939622459156386080305634677080506350249632630514863938445888806223951124355094468682539815309458151531117637927820629042605402188751144912274644498695897277")
g = 986762276114520220801525811758560961667498483061127810099097

# Function to query one get_bit(i) request and return integer value.
def query_bit(sock_file, i):
    req = json.dumps({"option": "get_bit", "i": i})
    sock_file.write(req+"\n")
    sock_file.flush()
    line = sock_file.readline().strip()
    if not line:
        raise Exception("Connection closed unexpectedly")
    data = json.loads(line)
    if "bit" not in data:
        raise Exception("Error from server: " + str(data))
    # The server returns the number as a hex string.
    return int(data["bit"], 16)

# Test whether x is in <g> by checking if it equals g^r mod N for some small r.
def is_power_of_g(x, limit=10000):
    for r in range(1, limit):
        if pow(g, r, N) == x:
            return True
    return False

def main():
    s = socket.create_connection((HOST, PORT))
    sock_file = s.makefile(mode="rw")
    
    # Read any welcome message
    welcome = sock_file.readline().strip()
    print(welcome)
    
    # Since FLAG is unknown length we assume it’s about 43 bytes (adjust if needed)
    flag_nbits = 43 * 8
    flag_bits = [0]*flag_nbits

    print("[*] Querying oracle for each bit index...")
    for i in range(flag_nbits):
        # Query twice for each bit index.
        try:
            res1 = query_bit(sock_file, i)
            res2 = query_bit(sock_file, i)
        except Exception as ex:
            print("Error:", ex)
            break

        # Compute ratio = res1 / res2 mod N.
        try:
            inv_res2 = inverse(res2, N)
        except Exception:
            ratio = 0
        else:
            ratio = (res1 * inv_res2) % N

        # If ratio is a (small) power of g then conclude that bit is 1.
        if is_power_of_g(ratio):
            flag_bits[i] = 1
            print(f"[*] Bit {i}: 1")
        else:
            flag_bits[i] = 0
            print(f"[*] Bit {i}: 0")

    # Reassemble bytes (note: bit i corresponds to bit (i % 8) in the byte; the challenge uses bit 0 as LSB)
    flag_bytes = bytearray()
    for j in range(0, flag_nbits, 8):
        byte_val = 0
        for bit in range(8):
            byte_val |= flag_bits[j+bit] << bit
        flag_bytes.append(byte_val)
    print("\nFLAG:", flag_bytes)
    s.close()

if __name__ == '__main__':
    main()