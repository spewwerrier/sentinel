import iptypes
import socket
import sys
from bcc import BPF
import ctypes

incoming_socket = None
INCOMING_PORT = 7777

SOCKET_ADDR = "127.0.0.1"

def callback(data, size, isblocked):
    if size == 8:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv4Pkt)).contents
        ipv4_address = "%d.%d.%d.%d" % (
            ((event.saddr >> 0) & 0xFF),
            ((event.saddr >> 8) & 0xFF),
            ((event.saddr >> 16) & 0xFF),
            ((event.saddr >> 24) & 0xFF),
        )
        if(isblocked):
            log_message = f""" {{ "ip": "{ipv4_address}", "packet": {event.pkt_size}, "blocked": "True" }} """
        else:
            log_message = f""" {{ "ip": "{ipv4_address}", "packet": {event.pkt_size}, "blocked": "False" }} """

        print(log_message)
    else:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv6Pkt)).contents
        ipv6_address = socket.inet_ntop(socket.AF_INET6, event.saddr.s6_addr)
        if(isblocked):
            log_message = f""" {{ "ip": "{ipv6_address}", "packet": {event.pkt_size}, "blocked": "True" }} """
        else:
            log_message = f""" {{ "ip": "{ipv6_address}", "packet": {event.pkt_size}, "blocked": "False" }} """
        print(log_message)

    try:
        incoming_socket.sendto(log_message.encode('utf-8'), (SOCKET_ADDR, INCOMING_PORT))
    except socket.error as e:
        print(f"Error sending data: {e}")


class Logger:
    def __init__(self, bpf:BPF):
        self.bpf = bpf

    # outputs incoming ip addresses in 7777
    def log(self):
        global incoming_socket
        try:
            incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as e:
            print(f"Error creating initial output socket: {e}")
            return

        incoming_callback = lambda ctx, data, size: callback(data, size, False)
        self.bpf["incoming_ipv4"].open_ring_buffer(incoming_callback)
        self.bpf["incoming_ipv6"].open_ring_buffer(incoming_callback)

        blocked_callback = lambda ctx, data, size: callback(data, size, True)
        self.bpf["blocked_ipv4"].open_ring_buffer(blocked_callback)
        self.bpf["blocked_ipv6"].open_ring_buffer(blocked_callback)

