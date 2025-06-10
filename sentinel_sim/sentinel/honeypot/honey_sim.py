import socket
import time

def simulate_connection(target_host='127.0.0.1', target_port=8080, attempts=5, delay=1):
    """Simulates repeated connection attempts to a honeypot."""
    for i in range(attempts):
        try:
            print(f"[+] Attempt {i+1} - Connecting to {target_host}:{target_port}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_host, target_port))
            
            # Optional: Send a fake request
            sock.sendall(b"GET / HTTP/1.1\r\nHost: honeypot\r\n\r\n")
            sock.close()
            time.sleep(delay)
        except Exception as e:
            print(f"[!] Connection failed: {e}")

if __name__ == "__main__":
    simulate_connection()
