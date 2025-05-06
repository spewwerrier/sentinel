import iptypes
import socket
import sys
from bcc import BPF
import ctypes

def incomingCallback(ctx, data, size):
    if(size == 8):
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv4Pkt)).contents
        print("Ipv4 %d.%d.%d.%d %d" % (
    			((event.saddr >> 0) & 0xFF),
    			((event.saddr >> 8) & 0xFF),
    			((event.saddr >> 16) & 0xFF),
    			((event.saddr >> 24) & 0xFF),
                event.pkt_size))
    else:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv6Pkt)).contents
        ipv6_address = socket.inet_ntop(socket.AF_INET6, event.saddr.s6_addr)
        print(f"ipv6 source: {ipv6_address}, packet size: {event.pkt_size}")


def blockedCallback(ctx, data, size):
    if(size == 8):
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv4Pkt)).contents
        print("Blocked Ipv4 %d.%d.%d.%d %d" % (
    			((event.saddr >> 0) & 0xFF),
    			((event.saddr >> 8) & 0xFF),
    			((event.saddr >> 16) & 0xFF),
    			((event.saddr >> 24) & 0xFF),
                event.pkt_size))
    else:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv6Pkt)).contents
        ipv6_address = socket.inet_ntop(socket.AF_INET6, event.saddr.s6_addr)
        print(f"Blocked ipv6 source: {ipv6_address}, packet size: {event.pkt_size}")
        

def incoming(b: BPF):
    b["incoming_ipv4"].open_ring_buffer(incomingCallback)
    b["incoming_ipv6"].open_ring_buffer(incomingCallback)

def blocked(b: BPF):
    b["blocked_ipv4"].open_ring_buffer(blockedCallback)
    b["blocked_ipv6"].open_ring_buffer(blockedCallback)
