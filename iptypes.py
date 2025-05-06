import ctypes

class IPv4Pkt(ctypes.Structure):
    _fields_ = [
        ("saddr", ctypes.c_uint32),
        ("pkt_size", ctypes.c_uint32)
    ]

class IPv6Addr(ctypes.Structure):
    _fields_ = [
        ("high", ctypes.c_uint64),
        ("low", ctypes.c_uint64),
    ]

class in6_addr(ctypes.Structure):
    _fields_ = [
        ("s6_addr", ctypes.c_uint8 * 16),
    ]
    
class IPv6Pkt(ctypes.Structure):
    _fields_ = [
        ("saddr", in6_addr),
        ("pkt_size", ctypes.c_uint32),
    ]
