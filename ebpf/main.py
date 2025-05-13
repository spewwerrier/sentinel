#!/usr/bin/env python
from bcc import BPF
import time
import socket
import struct
import sys
import ctypes
import threading

import logger
import iptypes
import blocker

iface = None
try:
    iface = sys.argv[1]
except:
    print("Network interface undefined. You can find one using `ip a`")
    sys.exit(1)

b = BPF(text=open('packet.ebpf.c', 'r').read())
# iface = "wlp3s0"
# iface = interface
fn = b.load_func("handle_rx", BPF.XDP)

try:
    b.attach_xdp(iface, fn, BPF.XDP_FLAGS_SKB_MODE)
except Exception as e:
    print(f"Failed to attach BPF program: {e}")
    sys.exit(1)

# we define what logging we want to enable, enabling both is okay
log = logger.Logger(b)
log.log()

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def listen_ip():
    server_address = ('localhost', 7779)
    listen_socket.settimeout(0.5)
    listen_socket.bind(server_address)
    print(f"listening for ip at 7779")
    while True:
        try:
            recv_socket, address = listen_socket.recvfrom(4096)
            utf_data = recv_socket.decode('utf-8')
            if (":" in utf_data):
                blocker.block_ipv6(b, utf_data)
            elif ("." in utf_data):
                blocker.block_ipv4(b, utf_data)
            else:
                blacklist_protocol = b["blacklist_protocol"]
                blacklist_protocol[ctypes.c_uint8(int(recv_socket.decode('utf-8')))] = ctypes.c_bool(True)
            print(f"blocking ip {recv_socket.decode('utf-8')}")
        except socket.timeout:
            continue
        except OSError as e:
            # we get bad file descriptor (error 9) when we close the socket which we do
            # on KeyboardInterrupt (ctrl-c) in main thread
            # so instead of erring we just cleanly exit from the while loop
            if e.errno == 9:
                print("Socket is closed")
                return
            print(f"Failed to receive on socket {e}")
        except Exception as e:
            print(f"Something went wrong on socket {e}")
            

listen_thread = threading.Thread(target=listen_ip)
listen_thread.start()

try:
    print("Running... (Ctrl+C to stop)")
    while True:
        b.ring_buffer_poll()
        time.sleep(0.1)
except KeyboardInterrupt:
    b.remove_xdp(iface, BPF.XDP_FLAGS_SKB_MODE)
    print("Detached BPF program.")
    listen_socket.close()
    print("Closed UDP socket.")
    listen_thread.join()
    print("Closed the socket thread")
