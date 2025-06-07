
# function/plot_generator.py

import sys
import os
import matplotlib.pyplot as plt
import django

# ---- Django setup ----
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel.settings')
django.setup()

from server.models import IPV4_Packet

# ---- Get the saddr from command line ----
if len(sys.argv) != 2:
    print("Usage: python plot_generator.py <saddr>")
    sys.exit(1)

saddr = sys.argv[1]

# ---- Query the database ----
packets = IPV4_Packet.objects.filter(saddr=saddr)
sizes = [p.pkt_size for p in packets]

if not sizes:
    print("No data for", saddr)
    sys.exit(0)

# ---- Plotting ----
plt.figure(figsize=(8, 5))
plt.hist(sizes, bins=10, color='skyblue', edgecolor='black')
plt.title(f"Packet Sizes for {saddr}")
plt.xlabel("Packet Size")
plt.show()

# ---- Save to static/plot.png --
