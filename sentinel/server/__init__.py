import socket

sock_incoming = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 7777)
try:
    sock_incoming.bind(server_address)
    print(f"Socket bound to ('localhost', 7777)")
    print(f"Socket object in __init__: {sock_incoming}")
except socket.error as e:
    print(f"{e} double connection")


sock_block = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 7778)
try:
    sock_block.bind(server_address)
    print(f"Socket bound to ('localhost', 7777)")
    print(f"Socket object in __init__: {sock_block}")
except socket.error as e:
    print(f"{e} double connection")

