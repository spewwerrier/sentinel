import socket

# Proxy server details
PROXY_HOST = 'localhost'
PROXY_PORT = 8080

# The HTTP request we want to send
HTTP_REQUEST = """GET / HTTP/1.1
Host: www.google.com
Connection: close
"""

def connect_to_proxy():
    # Create a socket to connect to the proxy server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((PROXY_HOST, PROXY_PORT))
    
    print(f"Connected to proxy server at {PROXY_HOST}:{PROXY_PORT}")

    # Send the HTTP request to the proxy server
    client_socket.sendall(HTTP_REQUEST.encode('utf-8'))

    # Receive the response from the proxy server (which is forwarded from the target server)
    response = b""
    while True:
        part = client_socket.recv(4096)
        if not part:
            break
        response += part

    print("Response from proxy server:")
    print(response.decode('utf-8', errors='ignore'))

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    connect_to_proxy()
