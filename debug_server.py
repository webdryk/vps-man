#!/usr/bin/env python3
import socket

def run_debug_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5353))
    print("DEBUG SERVER READY (UDP 5353)")
    
    try:
        while True:
            data, addr = sock.recvfrom(65535)
            print(f"📥 RAW DATA FROM {addr}: {data[:100]}...")
            sock.sendto(b"TEST RESPONSE", addr)
    except KeyboardInterrupt:
        print("\n🛑 Debug server shutting down")
    finally:
        sock.close()

if __name__ == "__main__":
    run_debug_server()