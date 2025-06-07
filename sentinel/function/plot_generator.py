# function/plot_generator.py
import sys
import os
import matplotlib.pyplot as plt
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from server.models import IPV4_Packet

def main(saddr):
    packets = IPV4_Packet.objects.filter(saddr=saddr)
    sizes = [p.pkt_size for p in packets]

    if not sizes:
        print("No data")
        return

    plt.figure()
    plt.hist(sizes, bins=10, color='skyblue')
    plt.title(f'Packet Sizes for {saddr}')
    plt.xlabel('Packet Size')
    plt.ylabel('Frequency')

    output_path = os.path.join('static', 'plot.png')
    plt.savefig(output_path)
    print("OK")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])

