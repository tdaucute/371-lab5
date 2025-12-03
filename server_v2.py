"""TODO: Make the server more secure against side-channel attacks"""

import socket, time
from pathlib import Path
import random 

SOCK_PATH = "/tmp/passwordchecker.sock"
Path(SOCK_PATH).unlink(missing_ok=True)

SECRET = b"S3cret!"
DELAY_PER_MATCH = 0.0008 

def vulnerableCompare(secret: bytes, candidate: bytes) -> bool:
    for i in range(min(len(secret), len(candidate))):
        if secret[i] != candidate[i]:
            return False
        time.sleep(DELAY_PER_MATCH)
    return len(secret) == len(candidate)


def compare_whole_string(secret, candidate):  # Compare the whole string instead of each byte using XOR
    compare = 0

    if len(secret) != len(candidate):
        return False
    
    for i in range(len(secret)):
        compare |= secret[i] ^ candidate[i]
    
    return compare == 0


def pad_time(secret, candidate):  # Add more time to sleep() to equalize time spent for both matches and mismatches
    threshold = 0.0005

    begin = time.perf_counter()
    compare = vulnerableCompare(secret, candidate)
    end = time.perf_counter()
    spent = end - begin

    if spent < threshold:
        time.sleep(threshold-spent)

    return compare
                

def jitter(secret, candidate):  # Add random noise to each comparison
    for i in range(len(candidate)):
        if secret[i] != candidate[i]:
            time.sleep(random.uniform(0.0001, 0.001))
            return False
        time.sleep(random.uniform(0.0001, 0.001))

    return len(secret) == len(candidate)


with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind(SOCK_PATH)
    s.listen(1)
    print("Listening on:", SOCK_PATH)
    while True:
        conn, _ = s.accept()
        with conn:
            data = conn.recv(1024)
            if not data:
                continue
            candidate = data.strip()
            #ok = compare_whole_string(SECRET, candidate)
            #ok = pad_time(SECRET, candidate)
            ok = jitter(SECRET, candidate)
            conn.sendall(b"1" if ok else b"0")
