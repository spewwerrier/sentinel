import iptypes
import socket
import sys
from bcc import BPF
import ctypes

incoming_socket = None
INCOMING_PORT = 7777
blocked_socket = None
BLOCKED_PORT = 7778

SOCKET_ADDR = "127.0.0.1"

def callback(data, size, output_socket, dest_port):
    if size == 8:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv4Pkt)).contents
        ipv4_address = "%d.%d.%d.%d" % (
            ((event.saddr >> 0) & 0xFF),
            ((event.saddr >> 8) & 0xFF),
            ((event.saddr >> 16) & 0xFF),
            ((event.saddr >> 24) & 0xFF),
        )


        log_message = f""" {{ "ip": "{ipv4_address}", "packet": {event.pkt_size} }} """
        # log_message = f"Ipv4 {ipv4_address}, packet size: {event.pkt_size}"
    else:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv6Pkt)).contents
        ipv6_address = socket.inet_ntop(socket.AF_INET6, event.saddr.s6_addr)
        log_message = f""" {{ "ip": "{ipv6_address}", "packet": {event.pkt_size} }} """
        # log_message = f"Ipv6 {ipv6_address}, packet size: {event.pkt_size}"

    try:
        output_socket.sendto(log_message.encode('utf-8'), (SOCKET_ADDR, dest_port))
    except socket.error as e:
        print(f"Error sending data: {e}")

def incoming(b: BPF):
    global incoming_socket
    try:
        incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        print(f"Error creating initial output socket: {e}")
        return

    incoming_callback = lambda ctx, data, size: callback(data, size, incoming_socket, INCOMING_PORT)
    b["incoming_ipv4"].open_ring_buffer(incoming_callback)
    b["incoming_ipv6"].open_ring_buffer(incoming_callback)

def blocked(b: BPF):
    global blocked_socket
    try:
        blocked_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        print(f"Error creating initial output socket: {e}")
        return

    blocked_callback = lambda ctx, data, size: callback(data, size, blocked_socket, BLOCKED_PORT)
    b["blocked_ipv4"].open_ring_buffer(blocked_callback)
    b["blocked_ipv6"].open_ring_buffer(blocked_callback)
