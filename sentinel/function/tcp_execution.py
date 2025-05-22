from scapy.all import IP, TCP, sr
import sys

target_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.1"
ports = [22, 80, 443, 3306]
packet = IP(dst=target_ip) / TCP(dport=ports, flags="S")
ans, _ = sr(packet, timeout=2, retry=1, verbose=0)

for sent, received in ans:
    if received.haslayer(TCP) and received[TCP].flags == "SA":
        print(f"{received[IP].src} {received[TCP].sport}")

