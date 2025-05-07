import socket

# there is an ebpf server that is responsible for communicating the ip addresses
# it is also responsible for blocking and logging ip addresses

# there are 2 sockets the ebpf program expects
# 1 for incoming messages
# 1 for sending messages to ebpf program on what to block

# socket that receives all the blocked and unblocked ip addresses
sock_incoming = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 7777)
try:
    sock_incoming.bind(server_address)
    print(f"Socket bound to ('localhost', 7777)")
    print(f"Socket object in __init__: {sock_incoming}")
except socket.error as e:
    print(f"{e} double connection")


# socket for sending what to block from the server
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
