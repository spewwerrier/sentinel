from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.template import loader
import subprocess
import os
import sys
from django.conf import settings
from server.models import IPV4_Packet

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
 packets = IPV4_Packet.objects.all()
 saddr_list=IPV4_Packet.objects.values_list('saddr',flat=True).distinct()
 selected = None
 graph_url = None  # We'll handle this in the next step

 return render(request, 'server/visualize.html', {
        'packets': packets,
        'saddr_list': saddr_list,
        'selected': selected,
        'graph_url': graph_url
    })

def analyze_saddr(request):
    saddr_list = IPV4_Packet.objects.values_list('saddr', flat=True).distinct()
    selected = None
    graph_url = None

    if request.method == "POST":
        selected = request.POST.get("saddr")
        script_path = os.path.join(settings.BASE_DIR, 'function', 'plot_generator.py')
        python_exec = sys.executable

        try:
            subprocess.run([python_exec, script_path, selected], check=True)
            graph_url = '/static/plot.png'
        except subprocess.CalledProcessError as e:
            graph_url = None

    return render(request, 'server/visualize.html', {
        'saddr_list': saddr_list,
        'selected': selected,
        'graph_url': graph_url,
    })
