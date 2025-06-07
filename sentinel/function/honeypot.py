import socket
import logging

# Setup logging
log_file_path = '/home/bodhi/Documents/sentinel/sentinel/function/honeypot.log'

logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def start_honeypot(host='0.0.0.0', port=8080):
    """Starts a simple TCP honeypot that logs incoming connections."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(1.0)  # Timeout every 1 second
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[+] Honeypot is running on {host}:{port}")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"[!] Connection from {client_address}")
                logging.info(f"Connection from {client_address}")
                client_socket.close()
            except socket.timeout:
                continue  # Check again for Ctrl+C
    except KeyboardInterrupt:
        print("\n[!] Honeypot stopped by user.")
        logging.info("Honeypot stopped by user.")
    except Exception as e:
        print(f"[!] Error: {e}")
        logging.error(f"Unexpected error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_honeypot()
