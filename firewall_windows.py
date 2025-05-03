import os
import json
import subprocess
import time
from datetime import datetime
import geoip2.database

CONFIG_PATH = "firewall_config.json"
LOG_PATH = "firewall_log.txt"
GEO_DB_PATH = "GeoLite2-City.mmdb"

seen_logs = set()

# Helper Functions

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"blocked_ips": [], "blocked_ports": [], "blocked_protocols": []}

def log_event(event):
    if event in seen_logs:
        return
    seen_logs.add(event)
    with open(LOG_PATH, "a") as log_file:
        log_file.write(event + "\n")

def get_country(ip):
    try:
        with geoip2.database.Reader(GEO_DB_PATH) as reader:
            response = reader.city(ip)
            return response.country.name
    except:
        return "Unknown"

def block_ip(ip):
    rule_name = f"Block_IP_{ip}"
    subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", "action=block", f"remoteip={ip}"], capture_output=True)
    country = get_country(ip)
    log_event(f"[{datetime.now()}] Blocked IP: {ip} ({country})")

def block_port(port):
    rule_name = f"Block_Port_{port}"
    subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", "action=block", f"localport={port}", "protocol=TCP"], capture_output=True)
    log_event(f"[{datetime.now()}] Blocked Port: {port}")

def block_protocol(proto):
    rule_name = f"Block_Proto_{proto}"
    subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", "action=block", f"protocol={proto}"], capture_output=True)
    log_event(f"[{datetime.now()}] Blocked Protocol: {proto}")

# Main Execution

config = load_config()

for ip in config.get("blocked_ips", []):
    block_ip(ip)

for port in config.get("blocked_ports", []):
    block_port(port)

for proto in config.get("blocked_protocols", []):
    block_protocol(proto)

print("Firewall rules enforced from configuration.")
