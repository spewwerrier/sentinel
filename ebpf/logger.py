import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import iptypes
import socket
import ctypes
from bcc import BPF

# Load the saved model and scaler
loaded_model = joblib.load('./sentinel/function/random_forest_model.pkl')
loaded_scaler = joblib.load('./sentinel/function/scaler.pkl')

# Re-initialize and fit the label encoder on the original 'Source IP' data
# Assuming 'data_original' dataframe is available from previous steps
try:
    label_encoder = LabelEncoder()
    label_encoder.fit(data_original['Source IP'])
except NameError:
    print("Error: 'data_original' not found. Please ensure the original data is loaded.")
    exit()

# Function to predict the label for the incoming packet
def predict_label(source_ip, destination_port, protocol, bwd_packet_length_max, urg_flag_count):
    new_data_dict = {
        'Source IP': [source_ip],
        'Destination Port': [destination_port],
        'Protocol': [protocol],
        'Bwd Packet Length Max': [bwd_packet_length_max],
        'URG Flag Count': [urg_flag_count],
    }

    new_data_point = pd.DataFrame(new_data_dict)

    try:
        # Apply label encoding to 'Source IP'
        new_data_point['Source IP'] = label_encoder.transform(new_data_point['Source IP'])
    except ValueError:
        print("Warning: Unseen Source IP encountered during encoding. Handle as needed.")
        new_data_point['Source IP'] = 0

    # Ensure the new data point has the same columns and order as the training data used by the scaler
    original_feature_names = loaded_scaler.feature_names_in_
    new_data_point_reindexed = new_data_point.reindex(columns=original_feature_names, fill_value=0)

    # Preprocess the new data point using the loaded scaler
    new_data_point_scaled = loaded_scaler.transform(new_data_point_reindexed)

    # Make a prediction using the loaded model
    prediction = loaded_model.predict(new_data_point_scaled)

    return prediction[0]

# Generate log message with the prediction label
def generate_log(ip, packet_size, port, urgent, isblocked, predicted_label):
    blockedFmt = "False"
    urgentFmt = "0"

    if urgent != 0:
        urgentFmt = "1"

    if isblocked:
        blockedFmt = "True"

    # Add prediction label to the log message
    if predicted_label == 0:
        prediction_label = "BENIGN"
    elif predicted_label == 1:
        prediction_label = "DDOS"
    else:
        prediction_label = "UNKNOWN"

    return f"""{{ "ip": "{ip}", "packet": "{packet_size}", "blocked": "{blockedFmt}", "port": {port}, "urg": {urgentFmt}, "prediction": "{prediction_label}" }}"""

# Callback function to log packet data
def callback(data, size, isblocked):
    if size == 12:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv4Pkt)).contents
        ipv4_address = "%d.%d.%d.%d" % (
            ((event.saddr >> 0) & 0xFF),
            ((event.saddr >> 8) & 0xFF),
            ((event.saddr >> 16) & 0xFF),
            ((event.saddr >> 24) & 0xFF),
        )
        
        # Predict label based on the packet features
        predicted_label = predict_label(ipv4_address, event.port, event.protocol, event.pkt_size, event.urg)
        
        # Generate log with prediction
        log_message = generate_log(ipv4_address, event.pkt_size, event.port, event.urg, isblocked, predicted_label)
        print(log_message)
    else:
        event = ctypes.cast(data, ctypes.POINTER(iptypes.IPv6Pkt)).contents
        ipv6_address = socket.inet_ntop(socket.AF_INET6, event.saddr.s6_addr)
        
        # Predict label based on the packet features
        predicted_label = predict_label(ipv6_address, event.port, event.protocol, event.pkt_size, event.urg)
        
        # Generate log with prediction
        log_message = generate_log(ipv6_address, event.pkt_size, event.port, event.urg, isblocked, predicted_label)
        print(log_message)

    try:
        # Send log to the server
        incoming_socket.sendto(log_message.encode("utf-8"), (SOCKET_ADDR, INCOMING_PORT))
    except socket.error as e:
        print(f"Error sending data: {e}")

class Logger:
    def __init__(self, bpf: BPF):
        self.bpf = bpf

    def log(self):
        global incoming_socket
        try:
            incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as e:
            print(f"Error creating initial output socket: {e}")
            return

        incoming_callback = lambda ctx, data, size: callback(data, size, False)
        self.bpf["incoming_ipv4"].open_ring_buffer(incoming_callback)
        self.bpf["incoming_ipv6"].open_ring_buffer(incoming_callback)

        blocked_callback = lambda ctx, data, size: callback(data, size, True)
        self.bpf["blocked_ipv4"].open_ring_buffer(blocked_callback)
        self.bpf["blocked_ipv6"].open_ring_buffer(blocked_callback)


