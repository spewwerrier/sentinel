import threading
import logging
import os
from scapy.all import sniff, TCP
from django.shortcuts import render
from django.http import HttpResponse

# Path to the log file
log_file_path = '/home/bodhi/Documents/sentinel/sentinel_sim/sentinel/intrusion_detection.log'

# Set up logging for IDS alerts (appending to the file)
logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_alert(message):
    logging.info(message)

# Counter for SYN packets
syn_count = 0

def detect_syn_flood(pkt):
    global syn_count
    if pkt.haslayer(TCP) and pkt[TCP].flags == "S":  # SYN flag set
        syn_count += 1
        print(f"SYN packet detected! Count: {syn_count}")

    # Define a threshold to alert for SYN Flood
    if syn_count > 10:  # Threshold for alerting
        alert_message = "ALERT: SYN flood attack detected!"
        print(alert_message)
        log_alert(alert_message)
        syn_count = 0  # Reset the count after alert

def start_sniffing():
    sniff(prn=detect_syn_flood, store=0)

# Start sniffing in the background
def run_sniffing_in_background():
    thread = threading.Thread(target=start_sniffing)
    thread.daemon = True  # Allow the thread to exit when the main program exits
    thread.start()

# Call this function once to start sniffing when Django starts
run_sniffing_in_background()

# View to show live packet detection stats (This can be static for now)
def live_detection(request):
    syn_count = 0  # You can replace this with the actual count from your background task

    # Alert message when threshold is exceeded (for display)
    alert_message = None
    if syn_count > 10:
        alert_message = "ALERT: SYN flood attack detected!"

    context = {
        'syn_count': syn_count,
        'alert_message': alert_message,
    }
    
    return render(request, 'intrusion_detection/live_detection.html', context)

# Read the latest log entries
def read_logs():
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            return log_file.readlines()[-10:]  # Get the last 10 log entries
    return []

# View to show the logs
def show_logs(request):
    logs = read_logs()
    return render(request, 'intrusion_detection/show_logs.html', {'logs': logs})

