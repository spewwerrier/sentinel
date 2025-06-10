import socket
import threading

# Target server details (replace with the actual target you want to forward requests to)
TARGET_IP = 'www.google.com'
TARGET_PORT = 80
LOCAL_PORT = 8080

def forward_ping(client_socket):
    try:
        # Receive the "ping" request from the client
        request = b""
        while True:
            part = client_socket.recv(1024)
            if not part:
                break
            request += part

        if not request:
            client_socket.close()
            return

        print(f"[+] Received ping request: {request.decode('utf-8', errors='ignore')}")
        
        # Connect to the target server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(10)
        print(f"[+] Forwarding ping request to {TARGET_IP}:{TARGET_PORT}")
        server_socket.connect((TARGET_IP, TARGET_PORT))

        # Forward the request (ping) to the target
        server_socket.send(request)

        # Receive the response from the target server
        response = b""
        while True:
            part = server_socket.recv(4096)
            if not part:
                break
            response += part

        if not response:
            print("[!] No response received from the target.")
            server_socket.close()
            client_socket.close()
            return

        # Send the response back to the client (acting like a proxy)
        print(f"[+] Forwarding response back to client.")
        client_socket.send(response)

        # Close the connections
        server_socket.close()
        client_socket.close()
    except Exception as e:
        print(f"[!] Error: {e}")
        client_socket.close()

def handle_client(client_socket, client_address):
    """Handles client connection in a separate thread."""
    print(f"[+] Connection from {client_address}")
    forward_ping(client_socket)

def start_proxy():
    # Create a socket to listen for incoming client connections
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind(('127.0.0.1', LOCAL_PORT))
    proxy_socket.listen(5)

    print(f"Proxy listening on port {LOCAL_PORT}, forwarding requests to {TARGET_IP}:{TARGET_PORT}")

    while True:
        try:
            client_socket, client_address = proxy_socket.accept()
            # Create a new thread to handle each client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        except Exception as e:
            print(f"[!] Error accepting connection: {e}")

if __name__ == "__main__":
    start_proxy()
