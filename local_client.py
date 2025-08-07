#!/usr/bin/env python3
import os
import socket
import sys
from cryptography.fernet import Fernet

class TunnelClient:
    def __init__(self, vps_ip='192.168.1.180', vps_port=5353):
        """Initialize the tunnel client"""
        self.vps_ip = vps_ip  # This should be your VPS IP address (e.g., '123.45.67.89')
        self.vps_port = vps_port
        
        # Initialize encryption
        self._setup_encryption()
        
        # Setup socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"🔌 Client initialized (will connect to {self.vps_ip}:{self.vps_port})")

    def _setup_encryption(self):
        """Initialize encryption from environment variable"""
        key_str = os.getenv('TUNNEL_KEY')
        
        if not key_str:
            print("❌ Error: TUNNEL_KEY environment variable not set!")
            print("Get the key from the server output and run:")
            print("export TUNNEL_KEY='your-key-here'")
            sys.exit(1)
            
        try:
            self.cipher = Fernet(key_str.encode('utf-8'))
            print(f"🔒 Encryption initialized (key: {key_str[:10]}...)")
        except ValueError as e:
            print(f"❌ Invalid key format: {e}")
            sys.exit(1)

    def send_message(self, message):
        """Send a message through the tunnel"""
        try:
            print(f"📤 Sending: {message[:50]}...")  # Show first 50 chars of message
            encrypted = self.cipher.encrypt(message.encode())
            
            # Send to VPS
            self.sock.sendto(encrypted, (self.vps_ip, self.vps_port))
            
            # Wait for response (5 second timeout)
            self.sock.settimeout(5.0)
            response, addr = self.sock.recvfrom(65535)
            decrypted = self.cipher.decrypt(response)
            print(f"📥 Received ({len(decrypted)} bytes): {decrypted.decode('utf-8')[:100]}...")
            
        except socket.timeout:
            print("⌛ Timeout - no response from server")
        except Exception as e:
            print(f"⚠️ Error: {str(e)[:100]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_client.py <message>")
        print("Example: python local_client.py 'Hello VPS!'")
        sys.exit(1)
        
    # Initialize client - REPLACE WITH YOUR ACTUAL VPS IP
    client = TunnelClient(vps_ip='192.168.1.180')  # e.g., '123.45.67.89'
    
    # Send message (combine all arguments)
    client.send_message(' '.join(sys.argv[1:]))