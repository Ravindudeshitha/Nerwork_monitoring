from collections import defaultdict
import pandas as pd
import threading
import time
import streamlit as st
from scapy.all import sniff

# Global flag for capturing
capturing_flag = False

# Use global dictionaries instead of modifying session state inside the thread
data_usage = defaultdict(lambda: defaultdict(int))  # Nested defaultdict to track source-destination pairs
captured_packets = []
ips = ['142.250.71.110', '34.139.124.58']

# Initialize session state if not already initialized
if "data_usage" not in st.session_state:
    st.session_state["data_usage"] = defaultdict(lambda: defaultdict(int))
if "captured_packets" not in st.session_state:
    st.session_state["captured_packets"] = []

# Packet processing function
def process_packet(packet):
    global data_usage, captured_packets
    if packet.haslayer("IP"):
        src_ip = packet["IP"].src
        dst_ip = packet["IP"].dst
        size = len(packet)

        # Track data usage for matching IPs or group under 'other'
        if src_ip in ips:
            data_usage[src_ip][dst_ip] += size  # Track data exchanged between src_ip and dst_ip
        
        if dst_ip in ips:
            data_usage[dst_ip][src_ip] += size  # Track data exchanged between dst_ip and src_ip

        if src_ip not in ips and dst_ip not in ips:
            data_usage['other'][src_ip] += size  # Group packets with non-matching IPs as 'other'
            data_usage['other'][dst_ip] += size  # Group packets with non-matching IPs as 'other'

        # Add the packet details to captured_packets
        captured_packets.append({
            "Source": src_ip,
            "Destination": dst_ip,
            "Size": size
        })

# Function to start packet sniffing
def start_sniffing():
    global capturing_flag
    while capturing_flag:
        sniff(prn=process_packet, iface="Ethernet 2", timeout=15, store=False)
        time.sleep(1)

# Function to print stats in the terminal every 15 seconds
def print_stats():
    global capturing_flag
    while capturing_flag:
        time.sleep(15)
        
        if data_usage:
            print("\n==== Network Traffic Stats (Last 15 sec) ====")
            
            # Print grouped IPs usage
            for ip, ip_data in data_usage.items():
                if ip != 'other':
                    print(f"Group {ip}:")
                    for dst_ip, total_bytes in ip_data.items():
                        print(f"  To {dst_ip}: Total Data: {total_bytes} bytes")
                else:
                    print(f"Other Group:")
                    for non_ip, total_bytes in ip_data.items():
                        print(f"  {non_ip}: Total Data: {total_bytes} bytes")
        else:
            print("\nNo packets captured in the last 15 seconds.")

        if captured_packets:
            print("\nCaptured Packets:")
            for pkt in captured_packets[-5:]:  # Print only last 5 packets
                print(f"Source: {pkt['Source']} → Destination: {pkt['Destination']}, Size: {pkt['Size']} bytes")
        print("==========================================\n")

# Function to start capture in a thread
def start_capture():
    global capturing_flag
    if not capturing_flag:
        capturing_flag = True
        thread1 = threading.Thread(target=start_sniffing, daemon=True)
        thread2 = threading.Thread(target=print_stats, daemon=True)
        thread1.start()
        thread2.start()

# Function to stop capturing
def stop_capture():
    global capturing_flag
    capturing_flag = False

# Streamlit UI
st.title("Network Traffic Monitor")

# Start/Stop Buttons
if st.button("Start Monitoring"):
    start_capture()
    st.success("Capturing packets... (updates every 15 seconds)")

if st.button("Stop Monitoring"):
    stop_capture()
    st.warning("Stopped capturing packets.")

# Button to refresh data without resetting it
if st.button("Refresh"):
    st.session_state["data_usage"] = dict(data_usage)
    st.session_state["captured_packets"] = captured_packets
    st.success("Data updated!")

# Show total data usage
st.subheader("Total Data Usage per IP")
df_usage = pd.DataFrame([(ip, dst_ip, total_bytes) for ip, ip_data in data_usage.items() for dst_ip, total_bytes in ip_data.items()], columns=["Source IP", "Destination IP", "Total Data (bytes)"])
st.dataframe(df_usage)

# IP Filtering
st.subheader("Filter by Specific IP")
filtered_ip = st.text_input("Enter IP to filter:")
if filtered_ip:
    filtered_packets = [pkt for pkt in st.session_state["captured_packets"] if pkt["Source"] == filtered_ip or pkt["Destination"] == filtered_ip]
    df_filtered = pd.DataFrame(filtered_packets)
    st.dataframe(df_filtered)

# Show all captured packets
st.subheader("Captured Packets")
df_packets = pd.DataFrame(st.session_state["captured_packets"])
st.dataframe(df_packets)


if st.session_state["captured_packets"]:
    st.subheader('Data Table')
    st.write(st.session_state["captured_packets"])
else:
    st.write('No data added yet.')
