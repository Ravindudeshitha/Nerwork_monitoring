# from flask import Flask, jsonify, request
# import socket
# import dns.resolver
# import json
# import threading
# import time
# import random
# import re
# from scapy.all import sniff, Ether, IP
# from collections import defaultdict
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# # Global storage
# data_list = []
# running = False
# capturing_flag = True

# MAC_FILE = 'mac_addresses.json'

# # Load MAC addresses from file
# def load_mac_addresses():
#     try:
#         with open(MAC_FILE, "r") as file:
#             return json.load(file)
#     except (FileNotFoundError, json.JSONDecodeError):
#         return []

# # Save MAC addresses to file
# def save_mac_addresses(mac_list):
#     with open(MAC_FILE, "w") as file:
#         json.dump(mac_list, file, indent=4)

# # Initialize MAC addresses
# mac_addresses = load_mac_addresses()

# data_usage = defaultdict(lambda: defaultdict(lambda: {'bytes': 0, 'ip': None, 'protocol': 'Unknown'}))
# captured_packets = []
# # mac_addresses = ['20:4e:f6:f4:a1:f3', '94:e7:0b:0e:0e:43']  # Lowercase MACs
# domain_ips = {}
# restricted_domain = []

# # Load domain IP mappings
# def load_domain_ips():
#     global domain_ips
#     try:
#         with open('domain_ips.json', 'r') as json_file:
#             domain_ips = json.load(json_file)
#     except FileNotFoundError:
#         domain_ips = {}

# def process_packet(packet):
#     global data_usage, captured_packets
#     if packet.haslayer(Ether):
#         src_mac = packet[Ether].src.lower()
#         dst_mac = packet[Ether].dst.lower()
#         size = len(packet)
        
#         src_ip = 'Unknown'
#         dst_ip = 'Unknown'
#         protocol = 'Unknown'
        
#         if packet.haslayer(IP):
#             ip_layer = packet[IP]
#             src_ip = ip_layer.src
#             dst_ip = ip_layer.dst
            
#             if ip_layer.proto == 6:
#                 protocol = "TCP"
#             elif ip_layer.proto == 17:
#                 protocol = "UDP"
#             elif ip_layer.proto == 1:
#                 protocol = "ICMP"
#             else:
#                 protocol = "Other-IP"

#         # Update data usage for monitored MACs
#         for mac in [src_mac, dst_mac]:
#             if mac in mac_addresses:
#                 target_ip = dst_ip if mac == src_mac else src_ip
#                 data_usage[mac][target_ip]['bytes'] += size
#                 data_usage[mac][target_ip]['ip'] = target_ip
#                 data_usage[mac][target_ip]['protocol'] = protocol

#         # Handle other traffic
#         if src_mac not in mac_addresses and dst_mac not in mac_addresses:
#             for ip in [src_ip, dst_ip]:
#                 data_usage['others'][ip]['bytes'] += size
#                 data_usage['others'][ip]['ip'] = ip
#                 data_usage['others'][ip]['protocol'] = protocol

#         # Store packet info
#         captured_packets.append({
#             "source_mac": src_mac,
#             "dest_mac": dst_mac,
#             "source_ip": src_ip,
#             "dest_ip": dst_ip,
#             "size": size,
#             "protocol": protocol
#         })

# def start_sniffing():
#     global capturing_flag
#     while capturing_flag:
#         sniff(prn=process_packet, iface="Wi-Fi", timeout=15, store=False)

# def get_formatted_data():
#     result = {}
    
#     # Add monitored MACs
#     for mac in mac_addresses:
#         result[mac] = {
#             ip: details['bytes']
#             for ip, details in data_usage[mac].items()
#         }
    
#     # Add others
#     result['others'] = {
#         ip: details['bytes']
#         for ip, details in data_usage['others'].items()
#     }
    
#     return result

# @app.route("/start", methods=["GET"])
# def start():
#     global running
#     if not running:
#         running = True
#         threading.Thread(target=start_sniffing, daemon=True).start()
#     return jsonify({"message": "Monitoring started!"})

# @app.route("/stop", methods=["GET"])
# def stop_monitoring():
#     global running, capturing_flag
#     if running:
#         # Stop the sniffing loop
#         capturing_flag = False
#         running = False
        
#         # Let the network thread finish gracefully
#         time.sleep(1)  
        
#         return jsonify({
#             "message": "Monitoring stopped successfully!",
#             "status": "stopped"
#         })
#     return jsonify({
#         "message": "Monitoring was not running!",
#         "status": "inactive"
#     })

# @app.route("/data", methods=["GET"])
# def get_data():
#     return jsonify(get_formatted_data())

# # @app.route("/data/<mac_address>", methods=["GET"])
# # def get_mac_data(mac_address):
# #     mac_address = mac_address.lower()  # Normalize MAC address format

# #     if mac_address in data_usage:
# #         return jsonify({mac_address: data_usage[mac_address]})
# #     else:
# #         return jsonify({"error": "MAC address not found"}), 404

# @app.route("/data/<mac_address>", methods=["GET"])
# def get_mac_data(mac_address):
#     mac_address = mac_address.lower()  # Normalize MAC address format

#     if mac_address in data_usage:
#         mac_data = data_usage[mac_address]

#         # Calculate total data usage
#         total_usage = sum(details["bytes"] for details in mac_data.values())

#         return jsonify({
#             mac_address: mac_data,
#             "total_bytes": total_usage
#         })
#     else:
#         return jsonify({"error": "MAC address not found"}), 404


# @app.route("/add_mac", methods=["POST"])
# def add_mac():
#     new_mac = request.json.get("mac", "").lower()
    
#     if not new_mac:
#         return jsonify({"error": "No MAC address provided"}), 400
    
#     # Validate MAC format
#     if not re.match(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$", new_mac):
#         return jsonify({"error": "Invalid MAC address format"}), 400
    
#     if new_mac not in mac_addresses:
#         mac_addresses.append(new_mac)
#         save_mac_addresses(mac_addresses)
#         return jsonify({
#             "message": f"MAC {new_mac} added successfully",
#             "current_macs": mac_addresses
#         })
    
#     return jsonify({
#         "message": f"MAC {new_mac} already exists",
#         "current_macs": mac_addresses
#     })

# @app.route("/macs", methods=["GET"])
# def list_macs():
#     return jsonify({"monitored_macs": mac_addresses})

# if __name__ == "__main__":
#     load_domain_ips()
#     threading.Thread(target=start_sniffing, daemon=True).start()
#     app.run(debug=True)

# from flask import Flask, jsonify, request
# import socket
# import dns.resolver
# import json
# import threading
# import time
# import random
# import re
# from scapy.all import sniff, Ether, IP
# from collections import defaultdict
# from flask_cors import CORS
# from scapy.all import sniff, Ether, IP, DNS, UDP

# from scapy.layers.http import HTTPRequest, HTTPResponse  # Import HTTP layers
# from scapy.all import TCP
# # from scapy.layers.tls.record import TLS

# app = Flask(__name__)
# CORS(app)

# # Global storage
# data_list = []
# running = False
# capturing_flag = True

# MAC_FILE = 'mac_addresses.json'

# # Load MAC addresses from file
# def load_mac_addresses():
#     try:
#         with open(MAC_FILE, "r") as file:
#             return json.load(file)
#     except (FileNotFoundError, json.JSONDecodeError):
#         return []

# # Save MAC addresses to file
# def save_mac_addresses(mac_list):
#     with open(MAC_FILE, "w") as file:
#         json.dump(mac_list, file, indent=4)

# # Initialize MAC addresses
# mac_addresses = load_mac_addresses()

# data_usage = defaultdict(lambda: defaultdict(lambda: {'bytes': 0, 'ip': None, 'protocol': 'Unknown'}))
# captured_packets = []
# # mac_addresses = ['20:4e:f6:f4:a1:f3', '94:e7:0b:0e:0e:43']  # Lowercase MACs
# domain_ips = {}
# restricted_domain = []

# # Load domain IP mappings
# # def load_domain_ips():
# #     global domain_ips
# #     try:
# #         with open('domain_ips.json', 'r') as json_file:
# #             domain_ips = json.load(json_file)
# #     except FileNotFoundError:
# #         domain_ips = {}

# # # def process_packet(packet):
# #     global data_usage, captured_packets
# #     if packet.haslayer(Ether):
# #         src_mac = packet[Ether].src.lower()
# #         dst_mac = packet[Ether].dst.lower()
# #         size = len(packet)
        
# #         src_ip = 'Unknown'
# #         dst_ip = 'Unknown'
# #         protocol = 'Unknown'
        
# #         if packet.haslayer(IP):
# #             ip_layer = packet[IP]
# #             src_ip = ip_layer.src
# #             dst_ip = ip_layer.dst
            
# #             if ip_layer.proto == 6:
# #                 protocol = "TCP"
# #             elif ip_layer.proto == 17:
# #                 protocol = "UDP"
# #             elif ip_layer.proto == 1:
# #                 protocol = "ICMP"
# #             else:
# #                 protocol = "Other-IP"

# #         # Update data usage for monitored MACs
# #         for mac in [src_mac, dst_mac]:
# #             if mac in mac_addresses:
# #                 target_ip = dst_ip if mac == src_mac else src_ip
# #                 data_usage[mac][target_ip]['bytes'] += size
# #                 data_usage[mac][target_ip]['ip'] = target_ip
# #                 data_usage[mac][target_ip]['protocol'] = protocol

# #         # Handle other traffic
# #         if src_mac not in mac_addresses and dst_mac not in mac_addresses:
# #             for ip in [src_ip, dst_ip]:
# #                 data_usage['others'][ip]['bytes'] += size
# #                 data_usage['others'][ip]['ip'] = ip
# #                 data_usage['others'][ip]['protocol'] = protocol

# #         # Store packet info
# #         captured_packets.append({
# #             "source_mac": src_mac,
# #             "dest_mac": dst_mac,
# #             "source_ip": src_ip,
# #             "dest_ip": dst_ip,
# #             "size": size,
# #             "protocol": protocol
# #         })


# def save_domain_ips():
#     with open('domain_ips.json', 'w') as f:
#         json.dump(domain_ips, f, indent=4)

# def load_domain_ips():
#     global domain_ips
#     try:
#         with open('domain_ips.json', 'r') as json_file:
#             domain_ips = json.load(json_file)
#     except (FileNotFoundError, json.JSONDecodeError):
#         domain_ips = {}

# # def process_packet(packet):
# #     global data_usage, captured_packets, domain_ips
# #     if packet.haslayer(Ether):
# #         src_mac = packet[Ether].src.lower()
# #         dst_mac = packet[Ether].dst.lower()
# #         size = len(packet)
        
# #         src_ip = 'Unknown'
# #         dst_ip = 'Unknown'
# #         protocol = 'Unknown'
        
# #         if packet.haslayer(IP):
# #             ip_layer = packet[IP]
# #             src_ip = ip_layer.src
# #             dst_ip = ip_layer.dst
            
# #             if ip_layer.proto == 6:
# #                 protocol = "TCP"
# #             elif ip_layer.proto == 17:
# #                 protocol = "UDP"
# #             elif ip_layer.proto == 1:
# #                 protocol = "ICMP"
# #             else:
# #                 protocol = "Other-IP"

# #         # Process DNS responses to map domains to IPs
# #         if packet.haslayer(DNS) and packet.haslayer(UDP):
# #             dns = packet[DNS]
# #             if dns.qr == 1:  # DNS response
# #                 for answer in dns.an:
# #                     if answer.type == 1:  # A record
# #                         domain = answer.rrname.decode('utf-8').rstrip('.').lower()
# #                         ip = answer.rdata
# #                         if isinstance(ip, str):
# #                             domain_ips[ip] = domain
# #                             save_domain_ips()  # Save after update

# #         # Update data usage for monitored MACs
# #         for mac in [src_mac, dst_mac]:
# #             if mac in mac_addresses:
# #                 target_ip = dst_ip if mac == src_mac else src_ip
# #                 data_usage[mac][target_ip]['bytes'] += size
# #                 data_usage[mac][target_ip]['protocol'] = protocol

# #         # Handle other traffic
# #         if src_mac not in mac_addresses and dst_mac not in mac_addresses:
# #             for ip in [src_ip, dst_ip]:
# #                 data_usage['others'][ip]['bytes'] += size
# #                 data_usage['others'][ip]['protocol'] = protocol

# #         # Store packet info
# #         captured_packets.append({
# #             "source_mac": src_mac,
# #             "dest_mac": dst_mac,
# #             "source_ip": src_ip,
# #             "dest_ip": dst_ip,
# #             "size": size,
# #             "protocol": protocol
# #         })
        
        
# def process_packet(packet):
#     global data_usage, captured_packets, domain_ips

#     if packet.haslayer(Ether):
#         src_mac = packet[Ether].src.lower()
#         dst_mac = packet[Ether].dst.lower()
#         size = len(packet)
        
#         src_ip = 'Unknown'
#         dst_ip = 'Unknown'
#         protocol = 'Unknown'

#         if packet.haslayer(IP):
#             ip_layer = packet[IP]
#             src_ip = ip_layer.src
#             dst_ip = ip_layer.dst
            
#             if packet.haslayer(TCP):
#                 tcp_layer = packet[TCP]
#                 if tcp_layer.dport == 80 or tcp_layer.sport == 80:
#                     protocol = "HTTP"
#                 elif tcp_layer.dport == 443 or tcp_layer.sport == 443:
#                     protocol = "HTTPS"
#                 else:
#                     return  # Ignore non-HTTP/HTTPS traffic

#         # Store HTTP request details if available
#         http_info = None
#         if packet.haslayer(HTTPRequest):
#             http_layer = packet[HTTPRequest]
#             http_info = {
#                 "method": http_layer.Method.decode() if http_layer.Method else "UNKNOWN",
#                 "host": http_layer.Host.decode() if http_layer.Host else "UNKNOWN",
#                 "path": http_layer.Path.decode() if http_layer.Path else "UNKNOWN"
#             }
        
#         # Store packet information
#         captured_packets.append({
#             "source_mac": src_mac,
#             "dest_mac": dst_mac,
#             "source_ip": src_ip,
#             "dest_ip": dst_ip,
#             "size": size,
#             "protocol": protocol,
#             "http_info": http_info
#         })

#         # Update data usage
#         for mac in [src_mac, dst_mac]:
#             if mac in mac_addresses:
#                 target_ip = dst_ip if mac == src_mac else src_ip
#                 data_usage[mac][target_ip]['bytes'] += size
#                 data_usage[mac][target_ip]['protocol'] = protocol

#         # Store domain info
#         if src_ip not in domain_ips:
#             domain_ips[src_ip] = http_info['host'] if http_info and 'host' in http_info else None
#         if dst_ip not in domain_ips:
#             domain_ips[dst_ip] = http_info['host'] if http_info and 'host' in http_info else None
        
#         save_domain_ips()


# def start_sniffing():
#     global capturing_flag
#     while capturing_flag:
#         sniff(prn=process_packet, iface="Wi-Fi", timeout=15, store=False)

# # def get_formatted_data():
# #     result = {}
    
# #     # Add monitored MACs
# #     for mac in mac_addresses:
# #         result[mac] = {
# #             ip: details['bytes']
# #             for ip, details in data_usage[mac].items()
# #         }
    
# #     # Add others
# #     result['others'] = {
# #         ip: details['bytes']
# #         for ip, details in data_usage['others'].items()
# #     }
    
# #     return result


# def get_formatted_data():
#     result = {}
    
#     # Add monitored MACs
#     for mac in mac_addresses:
#         result[mac] = {}
#         for ip, details in data_usage[mac].items():
#             domain = domain_ips.get(ip, None)
#             result[mac][ip] = {
#                 'bytes': details['bytes'],
#                 'domain': domain,
#                 'protocol': details['protocol']
#             }
    
#     # Add others
#     result['others'] = {}
#     for ip, details in data_usage['others'].items():
#         domain = domain_ips.get(ip, None)
#         result['others'][ip] = {
#             'bytes': details['bytes'],
#             'domain': domain,
#             'protocol': details['protocol']
#         }
    
#     return result

# @app.route("/start", methods=["GET"])
# def start():
#     global running
#     if not running:
#         running = True
#         threading.Thread(target=start_sniffing, daemon=True).start()
#     return jsonify({"message": "Monitoring started!"})

# @app.route("/stop", methods=["GET"])
# def stop_monitoring():
#     global running, capturing_flag
#     if running:
#         # Stop the sniffing loop
#         capturing_flag = False
#         running = False
        
#         # Let the network thread finish gracefully
#         time.sleep(1)  
        
#         return jsonify({
#             "message": "Monitoring stopped successfully!",
#             "status": "stopped"
#         })
#     return jsonify({
#         "message": "Monitoring was not running!",
#         "status": "inactive"
#     })

# @app.route("/data", methods=["GET"])
# def get_data():
#     return jsonify(get_formatted_data())

# # @app.route("/data/<mac_address>", methods=["GET"])
# # def get_mac_data(mac_address):
# #     mac_address = mac_address.lower()  # Normalize MAC address format

# #     if mac_address in data_usage:
# #         return jsonify({mac_address: data_usage[mac_address]})
# #     else:
# #         return jsonify({"error": "MAC address not found"}), 404

# # @app.route("/data/<mac_address>", methods=["GET"])
# # def get_mac_data(mac_address):
# #     mac_address = mac_address.lower()  # Normalize MAC address format

# #     if mac_address in data_usage:
# #         mac_data = data_usage[mac_address]

# #         # Calculate total data usage
# #         total_usage = sum(details["bytes"] for details in mac_data.values())

# #         return jsonify({
# #             mac_address: mac_data,
# #             "total_bytes": total_usage
# #         })
# #     else:
# #         return jsonify({"error": "MAC address not found"}), 404

# @app.route("/data/<mac_address>", methods=["GET"])
# def get_mac_data(mac_address):
#     mac_address = mac_address.lower()

#     if mac_address in data_usage:
#         mac_data = {}
#         total_usage = 0

#         for ip, details in data_usage[mac_address].items():
#             domain = domain_ips.get(ip, None)
#             mac_data[ip] = {
#                 'bytes': details['bytes'],
#                 'domain': domain,
#                 'protocol': details['protocol']
#             }
#             total_usage += details['bytes']

#         return jsonify({
#             mac_address: mac_data,
#             "total_bytes": total_usage
#         })
#     else:
#         return jsonify({"error": "MAC address not found"}), 404


# @app.route("/add_mac", methods=["POST"])
# def add_mac():
#     new_mac = request.json.get("mac", "").lower()
    
#     if not new_mac:
#         return jsonify({"error": "No MAC address provided"}), 400
    
#     # Validate MAC format
#     if not re.match(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$", new_mac):
#         return jsonify({"error": "Invalid MAC address format"}), 400
    
#     if new_mac not in mac_addresses:
#         mac_addresses.append(new_mac)
#         save_mac_addresses(mac_addresses)
#         return jsonify({
#             "message": f"MAC {new_mac} added successfully",
#             "current_macs": mac_addresses
#         })
    
#     return jsonify({
#         "message": f"MAC {new_mac} already exists",
#         "current_macs": mac_addresses
#     })

# @app.route("/macs", methods=["GET"])
# def list_macs():
#     return jsonify({"monitored_macs": mac_addresses})

# if __name__ == "__main__":
#     load_domain_ips()
#     threading.Thread(target=start_sniffing, daemon=True).start()
#     app.run(debug=True)

from flask import Flask, jsonify, request
import socket
import dns.resolver
import json
import threading
import time
import random
import re
from scapy.all import sniff, Ether, IP
from collections import defaultdict
from flask_cors import CORS
from scapy.all import sniff, Ether, IP, DNS, UDP, TCP
from scapy.layers.http import HTTPRequest, HTTPResponse

app = Flask(__name__)
CORS(app)

# Global storage
data_list = []
running = False
capturing_flag = True

MAC_FILE = 'mac_addresses.json'
BLACKLIST_FILE = 'blacklist.json'

# Load MAC addresses from file
def load_mac_addresses():
    try:
        with open(MAC_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save MAC addresses to file
def save_mac_addresses(mac_list):
    with open(MAC_FILE, "w") as file:
        json.dump(mac_list, file, indent=4)

# Initialize MAC addresses
mac_addresses = load_mac_addresses()

data_usage = defaultdict(lambda: defaultdict(lambda: {'bytes': 0, 'ip': None, 'protocol': 'Unknown'}))
captured_packets = []
domain_ips = {}

# Blacklist management functions
def load_blacklist():
    try:
        with open(BLACKLIST_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'domains': [], 'ips': []}

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(blacklist, f, indent=4)

# Load domain IP mappings
def load_domain_ips():
    global domain_ips
    try:
        with open('domain_ips.json', 'r') as json_file:
            domain_ips = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        domain_ips = {}

def save_domain_ips():
    with open('domain_ips.json', 'w') as f:
        json.dump(domain_ips, f, indent=4)

def process_packet(packet):
    global data_usage, captured_packets, domain_ips

    if packet.haslayer(Ether):
        src_mac = packet[Ether].src.lower()
        dst_mac = packet[Ether].dst.lower()
        size = len(packet)
        
        src_ip = 'Unknown'
        dst_ip = 'Unknown'
        protocol = 'Unknown'

        if packet.haslayer(IP):
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                if tcp_layer.dport == 80 or tcp_layer.sport == 80:
                    protocol = "HTTP"
                elif tcp_layer.dport == 443 or tcp_layer.sport == 443:
                    protocol = "HTTPS"
                else:
                    return  # Ignore non-HTTP/HTTPS traffic

        http_info = None
        if packet.haslayer(HTTPRequest):
            http_layer = packet[HTTPRequest]
            http_info = {
                "method": http_layer.Method.decode() if http_layer.Method else "UNKNOWN",
                "host": http_layer.Host.decode() if http_layer.Host else "UNKNOWN",
                "path": http_layer.Path.decode() if http_layer.Path else "UNKNOWN"
            }
        
        captured_packets.append({
            "source_mac": src_mac,
            "dest_mac": dst_mac,
            "source_ip": src_ip,
            "dest_ip": dst_ip,
            "size": size,
            "protocol": protocol,
            "http_info": http_info
        })

        for mac in [src_mac, dst_mac]:
            if mac in mac_addresses:
                target_ip = dst_ip if mac == src_mac else src_ip
                data_usage[mac][target_ip]['bytes'] += size
                data_usage[mac][target_ip]['protocol'] = protocol

        if src_ip not in domain_ips:
            domain_ips[src_ip] = http_info['host'] if http_info and 'host' in http_info else None
        if dst_ip not in domain_ips:
            domain_ips[dst_ip] = http_info['host'] if http_info and 'host' in http_info else None
        
        save_domain_ips()

def start_sniffing():
    global capturing_flag
    while capturing_flag:
        sniff(prn=process_packet, iface="Wi-Fi", timeout=15, store=False)

def get_formatted_data():
    result = {}
    
    for mac in mac_addresses:
        result[mac] = {}
        for ip, details in data_usage[mac].items():
            domain = domain_ips.get(ip, None)
            result[mac][ip] = {
                'bytes': details['bytes'],
                'domain': domain,
                'protocol': details['protocol']
            }
    
    result['others'] = {}
    for ip, details in data_usage['others'].items():
        domain = domain_ips.get(ip, None)
        result['others'][ip] = {
            'bytes': details['bytes'],
            'domain': domain,
            'protocol': details['protocol']
        }
    
    return result

@app.route("/start", methods=["GET"])
def start():
    global running
    if not running:
        running = True
        threading.Thread(target=start_sniffing, daemon=True).start()
    return jsonify({"message": "Monitoring started!"})

@app.route("/stop", methods=["GET"])
def stop_monitoring():
    global running, capturing_flag
    if running:
        capturing_flag = False
        running = False
        time.sleep(1)  
        return jsonify({"message": "Monitoring stopped!", "status": "stopped"})
    return jsonify({"message": "Not running!", "status": "inactive"})

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(get_formatted_data())

@app.route("/data/<mac_address>", methods=["GET"])
def get_mac_data(mac_address):
    mac_address = mac_address.lower()

    if mac_address in data_usage:
        mac_data = {}
        total_usage = 0

        for ip, details in data_usage[mac_address].items():
            domain = domain_ips.get(ip, None)
            mac_data[ip] = {
                'bytes': details['bytes'],
                'domain': domain,
                'protocol': details['protocol']
            }
            total_usage += details['bytes']

        return jsonify({
            mac_address: mac_data,
            "total_bytes": total_usage
        })
    else:
        return jsonify({"error": "MAC address not found"}), 404

@app.route("/add_mac", methods=["POST"])
def add_mac():
    new_mac = request.json.get("mac", "").lower()
    
    if not re.match(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$", new_mac):
        return jsonify({"error": "Invalid MAC format"}), 400
    
    if new_mac not in mac_addresses:
        mac_addresses.append(new_mac)
        save_mac_addresses(mac_addresses)
        return jsonify({"message": f"MAC {new_mac} added", "macs": mac_addresses})
    
    return jsonify({"message": f"MAC {new_mac} exists", "macs": mac_addresses})

@app.route("/macs", methods=["GET"])
def list_macs():
    return jsonify({"monitored_macs": mac_addresses})

# New endpoints for blacklist management
@app.route("/blacklist", methods=["POST"])
def update_blacklist():
    data = request.get_json()
    new_domains = [d.strip().lower() for d in data.get('domains', [])]
    new_ips = [ip.strip() for ip in data.get('ips', [])]

    blacklist = load_blacklist()
    
    # Merge and deduplicate
    updated_domains = list(set(blacklist['domains'] + new_domains))
    updated_ips = list(set(blacklist['ips'] + new_ips))
    
    blacklist['domains'] = updated_domains
    blacklist['ips'] = updated_ips
    
    save_blacklist(blacklist)
    return jsonify({"message": "Blacklist updated", "blacklist": blacklist})

@app.route("/blacklist", methods=["GET"])
def get_blacklist():
    return jsonify(load_blacklist())

@app.route("/check_blacklist", methods=["GET"])
def check_blacklist_access():
    blacklist = load_blacklist()
    results = []
    
    for mac in mac_addresses:
        flagged = False
        if mac not in data_usage:
            results.append({"mac": mac, "accessed_blacklist": False})
            continue
            
        for ip in data_usage[mac].keys():
            if ip in blacklist['ips']:
                flagged = True
                break
            
            domain = domain_ips.get(ip, "")
            if domain in blacklist['domains']:
                flagged = True
                break
        
        results.append({"mac": mac, "accessed_blacklist": flagged})
    
    return jsonify(results)

if __name__ == "__main__":
    load_domain_ips()
    threading.Thread(target=start_sniffing, daemon=True).start()
    app.run(debug=True)