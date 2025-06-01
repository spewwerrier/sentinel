from scapy.all import Ether, ARP, srp

# do we need to manually assign ip? We only know 192.168 is known
# 192.168.2^8 * 2^ 8 = 65536 ips. These much ip we need to calculate????????????
# Example IP range to scan
ip_range = "192.168.101.5/24"

# Send ARP requests
packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)

# make this concurrent and srp like 20 times per time?? I wish this was golang.
# https://docs.python.org/3/library/concurrent.futures.html#module-concurrent.futures

ans, _ = srp(packet, timeout=2, verbose=0)

# Print IP MAC per line (plain)
for sent, received in ans:
    print(f"{received.psrc} {received.hwsrc}")

