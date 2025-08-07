# debug_server.py
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5353))
print("DEBUG SERVER READY")

while True:
    data, addr = sock.recvfrom(65535)
    print(f"📥 RAW DATA FROM {addr}: {data[:100]}...")
    sock.sendto(b"TEST RESPONSE", addr)
    