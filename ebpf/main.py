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

b = BPF(text=open('packet.ebpf.c', 'r').read())
iface = "wlp2s0"
fn = b.load_func("handle_rx", BPF.XDP)

try:
    b.attach_xdp(iface, fn, BPF.XDP_FLAGS_SKB_MODE)
except Exception as e:
    print(f"Failed to attach BPF program: {e}")
    sys.exit(1)

# we define what logging we want to enable, enabling both is okay
log = logger.Logger(b)
log.incoming()
log.blocked()

blacklist_protocol = b["blacklist_protocol"]
blacklist_protocol[ctypes.c_uint8(1)] = ctypes.c_bool(True)
blacklist_protocol[ctypes.c_uint8(58)] = ctypes.c_bool(True)

# we listen on port 7779 and expect ipv4 and ipv6 and block them
def listen_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 7779)
    sock.bind(server_address)
    print(f"listening for ip at 7779")
    while True:
        data, address = sock.recvfrom(4096)
        utf_data = data.decode('utf-8')
        if (":" in utf_data):
            blocker.block_ipv6(b, utf_data)
        else:
            blocker.block_ipv4(b, utf_data)
        print(f"blocking ip {data.decode('utf-8')}")


stop_event = threading.Event()
listen_thread = threading.Thread(target=listen_ip)
listen_thread.daemon = True
listen_thread.start()

try:
    print("Running... (Ctrl+C to stop)")
    while True:
        b.ring_buffer_poll()
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_event.set()
    listen_thread.join()
    pass

b.remove_xdp(iface, BPF.XDP_FLAGS_SKB_MODE)
print("Detached BPF program.")
