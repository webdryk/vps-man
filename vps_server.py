#!/usr/bin/env python3
import os
import socket
import threading
import sys
import time
from cryptography.fernet import Fernet, InvalidToken

class VPSTunnelServer:
    def __init__(self, listen_ip='0.0.0.0', listen_port=5353):
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.running = False
        self.stats = {
            'connections': 0,
            'errors': 0,
            'bytes_received': 0,
            'start_time': time.time()
        }
        
        # Initialize encryption and sockets
        self._setup_encryption()
        self._setup_sockets()
        
    def _setup_encryption(self):
        """Initialize encryption with environment variable or generated key"""
        key_str = os.getenv('TUNNEL_KEY')
        
        if not key_str:
            self.key = Fernet.generate_key()
            key_str = self.key.decode('utf-8')
            print(f"\n🔑 Generated NEW encryption key: {key_str}")
            print("⚠️  IMPORTANT: Set this on both client and server using:")
            print(f"   export TUNNEL_KEY='{key_str}'\n")
        else:
            self.key = key_str.encode('utf-8')
        
        try:
            self.cipher = Fernet(self.key)
            print(f"🔒 Encryption initialized (key: {self.key.decode('utf-8')[:10]}...)")
        except ValueError as e:
            print(f"❌ Invalid key format: {e}")
            print("Key must be 32 url-safe base64-encoded bytes")
            sys.exit(1)

    def _setup_sockets(self):
        """Initialize and configure network sockets"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.listen_ip, self.listen_port))
            print(f"🛜 Socket bound to {self.listen_ip}:{self.listen_port}")
        except socket.error as e:
            print(f"❌ Socket error: {e}")
            sys.exit(1)

    def _validate_packet(self, data):
        """Basic packet validation"""
        if len(data) < 10:  # Minimum encrypted packet size
            raise ValueError("Packet too small")
        if len(data) > 65535:
            raise ValueError("Packet too large")

    def handle_client(self, data, client_addr):
        """Handle incoming client requests"""
        self.stats['connections'] += 1
        
        try:
            self._validate_packet(data)
            self.stats['bytes_received'] += len(data)
            
            decrypted = self.cipher.decrypt(data)
            if not decrypted:
                raise ValueError("Empty decrypted data")
                
            print(f"📥 [{client_addr}] Received {len(decrypted)} bytes")
            
            # Process data (echo back for testing)
            response = f"ACK[{time.strftime('%H:%M:%S')}]: {decrypted.decode('utf-8', errors='replace')[:100]}"
            encrypted_response = self.cipher.encrypt(response.encode())
            
            self.sock.sendto(encrypted_response, client_addr)
            print(f"📤 [{client_addr}] Sent response ({len(encrypted_response)} bytes)")
            
        except InvalidToken as e:
            self.stats['errors'] += 1
            print(f"🔐 [{client_addr}] Decryption failed - wrong key?")
        except UnicodeDecodeError as e:
            self.stats['errors'] += 1
            print(f"📜 [{client_addr}] Encoding error: {e}")
        except Exception as e:
            self.stats['errors'] += 1
            print(f"⚠️  [{client_addr}] Error: {e}")
            import traceback
            traceback.print_exc()

    def start(self):
        """Start the server main loop"""
        self.running = True
        print(f"\n🚀 Server started on {self.listen_ip}:{self.listen_port}")
        print(f"🕒 Started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("⌛ Waiting for connections...\n")
        
        try:
            while self.running:
                data, addr = self.sock.recvfrom(65535)
                threading.Thread(
                    target=self.handle_client,
                    args=(data, addr),
                    daemon=True
                ).start()
                
        except KeyboardInterrupt:
            print("\n🛑 Server shutting down...")
        except Exception as e:
            print(f"❌ Fatal error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Cleanup resources"""
        self.running = False
        if hasattr(self, 'sock'):
            self.sock.close()
        print("\n📊 Server Statistics:")
        print(f"• Uptime: {time.time() - self.stats['start_time']:.2f} seconds")
        print(f"• Connections: {self.stats['connections']}")
        print(f"• Data received: {self.stats['bytes_received']} bytes")
        print(f"• Errors: {self.stats['errors']}")
        print("✅ Server shutdown complete")

if __name__ == "__main__":
    server = VPSTunnelServer()
    try:
        server.start()
    except Exception as e:
        print(f"Fatal initialization error: {e}")
        sys.exit(1)
        
        
        








        
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5353))
print("DEBUG SERVER READY")

while True:
    data, addr = sock.recvfrom(65535)
    print(f"📥 RAW DATA FROM {addr}: {data[:100]}...")
    sock.sendto(b"TEST RESPONSE", addr)
    