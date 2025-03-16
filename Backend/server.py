from flask import Flask, jsonify, request
import socket
import dns.resolver
import json
import threading
import time
import random
from scapy.all import sniff, Ether, IP
from collections import defaultdict
import pandas as pd

app = Flask(__name__)

# Global storage for data
data_list = []
running = False
capturing_flag = True

data_usage = defaultdict(lambda: defaultdict(lambda: {'bytes': 0, 'ip': None}))  # Store bytes & IP
captured_packets = []
mac_addresses = ['92:55:26:49:f1:7c', '94:e7:0b:0e:0e:43']
domain_ips = {} 
restricted_domain = []

# Load domain IP mappings from JSON file
def load_domain_ips():
    global domain_ips
    try:
        with open('domain_ips.json', 'r') as json_file:
            domain_ips = json.load(json_file)
    except FileNotFoundError:
        domain_ips = {}
        
def process_packet(packet):
    global data_usage, captured_packets
    if packet.haslayer(Ether):
        src_mac = packet[Ether].src
        dst_mac = packet[Ether].dst
        size = len(packet)
        src_ip = packet[IP].src if packet.haslayer(IP) else 'Unknown'
        dst_ip = packet[IP].dst if packet.haslayer(IP) else 'Unknown'
        
        # Get protocol type (use IP layer and check its protocol field)
        protocol = "Unknown"
        if packet.haslayer(IP):
            if packet[IP].proto == 6:
                protocol = "TCP"
            elif packet[IP].proto == 17:
                protocol = "UDP"
            elif packet[IP].proto == 1:
                protocol = "ICMP"
            else:
                protocol = "Other"
        
        # If source MAC is in the mac_addresses list
        if src_mac in mac_addresses:
            # Group by src_mac, but store packet size by destination IP
            if dst_ip not in data_usage[src_mac]:
                data_usage[src_mac][dst_ip] = {'bytes': 0, 'protocol': protocol}
            data_usage[src_mac][dst_ip]['bytes'] += size
            data_usage[src_mac][dst_ip]['ip'] = dst_ip  # Storing the destination IP address
            data_usage[src_mac][dst_ip]['protocol'] = protocol  # Save protocol type

        # If destination MAC is in the mac_addresses list
        if dst_mac in mac_addresses:
            # Group by dst_mac, but store packet size by source IP
            if src_ip not in data_usage[dst_mac]:
                data_usage[dst_mac][src_ip] = {'bytes': 0, 'protocol': protocol}
            data_usage[dst_mac][src_ip]['bytes'] += size
            data_usage[dst_mac][src_ip]['ip'] = src_ip  # Storing the source IP address
            data_usage[dst_mac][src_ip]['protocol'] = protocol  # Save protocol type

        # If neither source nor destination MAC are in the mac_addresses list, store it under 'other'
        if src_mac not in mac_addresses and dst_mac not in mac_addresses:
            if src_ip not in data_usage['other']:
                data_usage['other'][src_ip] = {'bytes': 0, 'protocol': protocol}
            if dst_ip not in data_usage['other']:
                data_usage['other'][dst_ip] = {'bytes': 0, 'protocol': protocol}
            
            data_usage['other'][src_ip]['bytes'] += size
            data_usage['other'][src_ip]['ip'] = src_ip  # Storing the source IP address
            data_usage['other'][src_ip]['protocol'] = protocol  # Save protocol type
            data_usage['other'][dst_ip]['bytes'] += size
            data_usage['other'][dst_ip]['ip'] = dst_ip  # Storing the destination IP address
            data_usage['other'][dst_ip]['protocol'] = protocol  # Save protocol type

        # Append the packet information for later display or analysis
        captured_packets.append({
            "Source MAC": src_mac,
            "Source IP": src_ip,
            "Destination MAC": dst_mac,
            "Destination IP": dst_ip,
            "Size": size,
            "Protocol": protocol  # Save protocol type with packet information
        })



def start_sniffing():
    global capturing_flag
    while capturing_flag:
        sniff(prn=process_packet, iface="Wi-Fi", timeout=15, store=False)
        time.sleep(1)

def print_stats():
    global capturing_flag
    while capturing_flag:
        time.sleep(15)
        print("\n==== Network Traffic Stats (Last 15 sec) ====")
        for mac, mac_data in data_usage.items():
            if mac != 'other':
                print(f"Group {mac}:")
                for dst_mac, details in mac_data.items():
                    print(f"  To {dst_mac} (IP: {details['ip']}): {details['bytes']} bytes")
            else:
                print("Other Group:")
                for non_mac, details in mac_data.items():
                    print(f"  {non_mac} (IP: {details['ip']}): {details['bytes']} bytes")

        if captured_packets:
            print("\nCaptured Packets:")
            for pkt in captured_packets[-5:]:
                print(f"{pkt['Source MAC']} ({pkt['Source IP']}) -> {pkt['Destination MAC']} ({pkt['Destination IP']}), Size: {pkt['Size']} bytes")
        print("==========================================\n")
        
# Function to generate data in a separate thread
def generate_data():
    global running
    counter = 1
    while running:
        new_object = {
            "name": f"Data {counter}",
            "mak": random.randint(1, 100),
            "time": time.strftime("%H:%M:%S")
        }
        data_list.append(new_object)
        counter += 1
        time.sleep(1)

def clean_domain(url):
    if url.startswith("https://"):
        url = url[8:]
    elif url.startswith("http://"):
        url = url[7:]
    return url.rstrip('/')

# Function to get IP addresses from domain
def get_ip_addresses(domain):
    ip_addresses = []

    try:
        ip = socket.gethostbyname(domain)
        ip_addresses.append(ip)
    except socket.gaierror:
        print(f"Could not resolve domain {domain} using socket.")
    
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for answer in answers:
            ip_addresses.append(answer.to_text())
    except dns.resolver.NoAnswer:
        print(f"No A records found for domain {domain}.")
    except dns.resolver.NXDOMAIN:
        print(f"Domain {domain} does not exist.")
    
    return ip_addresses

# Save domain IPs to a JSON file
def save_domain_ips():
    with open('domain_ips.json', 'w') as json_file:
        json.dump(domain_ips, json_file, indent=4)

def get_restricted_macs(data_usage, domain_file):
    # Load domain data from JSON file
    with open(domain_file, 'r') as file:
        domain_data = json.load(file)
    
    # Reverse map: IP -> Domain
    ip_to_domain = {}
    for domain, ip_list in domain_data.items():
        for ip in ip_list:
            ip_to_domain[ip] = domain
    
    restricted = {}
    
    # Check each MAC's data usage
    for mac, usage_data in data_usage.items():
        mac_domains = set()
        for ip, details in usage_data.items():
            if ip in ip_to_domain:
                mac_domains.add(ip_to_domain[ip])
        
        if mac_domains:
            restricted[mac] = mac_domains
    
    return restricted

def pp():
    domain_file = "domain_ips.json"
    restricted_macs = get_restricted_macs(data_usage, domain_file)
    print(restricted_macs)
    
# Route to submit domain and save its IPs
@app.route("/save_domain", methods=["POST"])
def save_domain():
    domain = request.json.get("domain")
    if domain:
        cleaned_domain = clean_domain(domain)
        ips = get_ip_addresses(cleaned_domain)
        if ips:
            domain_ips[cleaned_domain] = ips
            save_domain_ips()
            return jsonify({"message": f"IP addresses for {cleaned_domain} saved!"})
        else:
            return jsonify({"message": f"No IP addresses found for {cleaned_domain}."}), 404
    return jsonify({"message": "No domain provided."}), 400


# Route to start data generation
@app.route("/start", methods=["GET"])
def start():
    global running
    
    if not running:
        running = True
        threading.Thread(target=start_sniffing, daemon=True).start()
        threading.Thread(target=print_stats, daemon=True).start()
    return jsonify({"message": "Data generation started!"})

# Route to fetch data
@app.route("/data", methods=["GET"])
def get_data():
    pp()
    return jsonify(data_usage)

if __name__ == "__main__":
    app.run(debug=True)
