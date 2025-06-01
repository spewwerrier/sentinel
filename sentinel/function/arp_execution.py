from scapy.all import Ether, ARP, srp
import socket

ipaddr = socket.gethostbyname(socket.gethostname())
# seems like you only need first 3 octets
ip_range = ".".join(ipaddr.split(".")[:-1] + ["1/24"])

# ip_range = "192.168.101.1/24"

# Send ARP requests
packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)

# make this concurrent and srp like 20 times per time?? I wish this was golang.
# https://docs.python.org/3/library/concurrent.futures.html#module-concurrent.futures

ans, _ = srp(packet, timeout=2, verbose=0)

# Print IP MAC per line (plain)
for sent, received in ans:
    print(f"{received.psrc} {received.hwsrc}")
