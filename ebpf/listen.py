import socket
blocked = 7778
incoming = 7777

def receive_udp_data(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', port)
    sock.bind(server_address)

    print(f"Listening for UDP data on port {port}")

    try:
        while True:
            data, address = sock.recvfrom(4096)
            print(f"{data.decode('utf-8')}")
    except KeyboardInterrupt:
        print("\nShutting down the listener...")
    finally:
        sock.close()


receive_udp_data(incoming)
