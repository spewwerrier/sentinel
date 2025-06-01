from scapy.all import IP, TCP, sr
import socket
import sys

ipaddr = socket.gethostbyname(socket.gethostname())
ip = ".".join(ipaddr.split(".")[:-1] + ["1"])



target_ip = sys.argv[1] if len(sys.argv) > 1 else ip
ports = [22, 80, 443, 3306, 8000]
packet = IP(dst=target_ip) / TCP(dport=ports, flags="S")
ans, _ = sr(packet, timeout=2, retry=1, verbose=0)

for sent, received in ans:
    if received.haslayer(TCP) and received[TCP].flags == "SA":
        print(f"{received[IP].src} {received[TCP].sport}")

