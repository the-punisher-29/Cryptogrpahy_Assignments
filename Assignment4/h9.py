#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/h9.py

import socket
import json
import sys

def run_challenge(hex_data, host="socket.cryptohack.org", port=13407):
    msg = {
        "option": "message",
        "data": hex_data
    }
    # Connect to the challenge server
    with socket.create_connection((host, port)) as sock:
        file_obj = sock.makefile("rw")
        # Send the JSON request
        file_obj.write(json.dumps(msg) + "\n")
        file_obj.flush()
        # Read the response line and parse the JSON data.
        response = file_obj.readline()
    return json.loads(response)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <hex_data>".format(sys.argv[0]))
        sys.exit(1)
    hex_data = sys.argv[1]
    response = run_challenge(hex_data)
    print("Response:", response)