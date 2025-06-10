import socket
import logging

# Setup logging
log_file_path = '//home/bodhi/Documents/sentinel/sentinel_sim/sentinel/honeypot/honeypot.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def start_honeypot(host='0.0.0.0', port=8080, max_connections=10):
    """Starts a simple TCP honeypot that logs incoming connections."""
    connection_count = 0  # Initialize connection counter
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(1.0)  # Timeout every 1 second
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[+] Honeypot is running on {host}:{port}")

        while connection_count < max_connections:  # Limit to max_connections
            try:
                client_socket, client_address = server_socket.accept()
                print(f"[!] Connection from {client_address}")
                logging.info(f"Connection from {client_address}")
                connection_count += 1  # Increment connection counter
                client_socket.close()
            except socket.timeout:
                continue  # Retry the accept in case of timeout

        print(f"[+] Reached max connections: {max_connections}. Stopping honeypot.")
        logging.info(f"Reached max connections: {max_connections}. Stopping honeypot.")
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
