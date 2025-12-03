import socket, time
from pathlib import Path

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
            ok = vulnerableCompare(SECRET, candidate)
            conn.sendall(b"1" if ok else b"0")
