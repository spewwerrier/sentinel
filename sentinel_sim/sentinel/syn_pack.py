from scapy.all import IP, TCP, send
import time

# Create a SYN packet
syn_packet = IP(dst="192.168.1.131")/TCP(dport=80, flags="S")  # Replace with the target IP

# Send 10 SYN packets
for _ in range(10):
    send(syn_packet)
    time.sleep(0.1)  # Add a small delay to avoid overwhelming the network
