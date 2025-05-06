import iptypes
import socket
import ctypes
import struct
from bcc import BPF
import ipaddress

def block_ipv4(b: BPF, ip: str):
    ip = int.from_bytes(socket.inet_aton(ip), "little")
    blacklist_ipv4 = b["blacklist_ipv4"]
    blacklist_ipv4[ctypes.c_int32(ip)] = ctypes.c_bool(True)

def block_ipv6(b: BPF, ip: str):
    ipv6 = ipaddress.IPv6Address(ip)
    high = int.from_bytes(ipv6.packed[:8], "big")
    low = int.from_bytes(ipv6.packed[8:], "big")
    blacklist_ipv6 = b["blacklist_ipv6"]
    blacklist_ipv6[iptypes.IPv6Addr(high, low)] = ctypes.c_bool(True)
