from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.template import loader
import subprocess
import os
import sys
from django.conf import settings
from server.models import IPV4_Packet
from django.utils.timezone import localtime
import calendar
import maxminddb


# in this program views.py are used for rendering a HTML template
# other request are done by ebpf_data.py
def index(request: HttpRequest):
    return render(request, 'server/index.html')


def filter_option(request: HttpRequest):
    return render(request, 'server/filter.html')


def network_scan_view(request):
    arp_result = []
    tcp_result = []

    if request.method == "POST":
        python_exec = sys.executable
        base = settings.BASE_DIR
        arp_script = os.path.join(base, 'function', 'arp_execution.py')
        tcp_script = os.path.join(base, 'function', 'tcp_execution.py')

        # ARP scan with sudo
        try:
            arp_output = subprocess.check_output(
                ['sudo', python_exec, arp_script],
                text=True
            )
            for line in arp_output.strip().splitlines():
                parts = line.strip().split()
                if len(parts) == 2:
                    arp_result.append({'ip': parts[0], 'mac': parts[1]})
        except subprocess.CalledProcessError as e:
            arp_result = [{'ip': 'Error', 'mac': e.output.strip()}]

        # TCP scan with sudo
        try:
            tcp_output = subprocess.check_output(
                ['sudo', python_exec, tcp_script],
                text=True
            )
            for line in tcp_output.strip().splitlines():
                parts = line.strip().split()
                if len(parts) == 2:
                    tcp_result.append({'ip': parts[0], 'port': parts[1]})
        except subprocess.CalledProcessError as e:
            tcp_result = [{'ip': 'Error', 'port': e.output.strip()}]

    return render(request, 'server/arp_scan.html', {
        'arp_result': arp_result,
        'tcp_result': tcp_result
    })


def honeypot_view(request):
    output = ""

    if request.method == "POST":
        python_exec = sys.executable
        base = settings.BASE_DIR
        honeypot_script = os.path.join(base, 'function', 'honeypot.py')  # adjust path if needed

        try:
            result = subprocess.run(
                [python_exec, honeypot_script],
                capture_output=True,
                text=True,
                timeout=10  # prevent hanging
            )
            output = result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            output = f"Error during execution: {e.output}"
        except Exception as e:
            output = f"Unhandled error: {str(e)}"

    return render(request, 'server/honey.html', {
        'output': output
    })


def visualize(request: HttpRequest):

    saddr_list = list(IPV4_Packet.objects.values_list('saddr', flat=True).distinct())
    saddr_list.insert(0, 'all') 


    selected = request.POST.get('saddr') if request.method == "POST" else 'all'


    packets = IPV4_Packet.objects.all() if selected == 'all' else IPV4_Packet.objects.filter(saddr=selected)


    sizes = [p.pkt_size for p in packets]
    size_counts = {}
    for size in sizes:
        size_counts[size] = size_counts.get(size, 0) + 1
    size_categories = sorted(size_counts.keys())
    size_frequencies = [size_counts[k] for k in size_categories]


    ports = [p.port for p in packets]
    port_counts = {}
    for port in ports:
        port_counts[port] = port_counts.get(port, 0) + 1
    port_scatter = [[port, port_counts[port]] for port in sorted(port_counts)]


    ip_list = sorted(set(p.saddr for p in packets))
    ip_index_map = {ip: i for i, ip in enumerate(ip_list)}
    ip_timestamp_scatter = [
        [calendar.timegm(localtime(p.timestamp).utctimetuple()) * 1000, ip_index_map[p.saddr]]
        for p in packets
    ]

    context = {
        'packets': packets,
        'saddr_list': saddr_list,
        'selected': selected,
        'size_categories': size_categories,
        'size_frequencies': size_frequencies,
        'port_scatter': port_scatter,
        'ip_timestamp_scatter': ip_timestamp_scatter,
        'ip_categories': ip_list,
    }

    return render(request, 'server/visualize.html', context)

def geoip_lookup(request):
    ip_address = None
    country = None
    city = None
    latitude = None
    longitude = None

    if request.method == 'POST':
        # Get IP address from form
        ip_address = request.POST.get('ip_address')

        # Check if IP address is provided
        if ip_address:
            try:
                # Open the GeoLite2 database
                with maxminddb.open_database('./sentinel/function/GeoLite2-City.mmdb') as reader:
                    result = reader.get(ip_address)

                # Extract the GeoIP data
                if result:
                    country = result.get('country', {}).get('names', {}).get('en', 'N/A')
                    city = result.get('city', {}).get('names', {}).get('en', 'N/A')
                    latitude = result.get('location', {}).get('latitude', 'N/A')
                    longitude = result.get('location', {}).get('longitude', 'N/A')
                else:
                    country = 'N/A'
                    city = 'N/A'
                    latitude = 'N/A'
                    longitude = 'N/A'
            except Exception as e:
                country = city = latitude = longitude = 'Error: ' + str(e)

    # Pass the result to the template
    context = {
        'ip_address': ip_address,
        'country': country,
        'city': city,
        'latitude': latitude,
        'longitude': longitude,
    }

    return render(request, 'server/geoip.html', context)
