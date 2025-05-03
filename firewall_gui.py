import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
from datetime import datetime

CONFIG_PATH = "firewall_config.json"
RULE_PREFIXES = {
    "ip": "Block_IP_",
    "port": "Block_Port_",
    "proto": "Block_Proto_"
}

# Helper Functions

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"blocked_ips": [], "blocked_ports": [], "blocked_protocols": []}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def add_to_config(value, key):
    config = load_config()
    if value not in config[key]:
        config[key].append(value)
        save_config(config)

def remove_from_config(value, key):
    config = load_config()
    if value in config[key]:
        config[key].remove(value)
        save_config(config)

def delete_firewall_rule(name):
    subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={name}"], capture_output=True)

def get_firewall_rules():
    output = subprocess.run(["netsh", "advfirewall", "firewall", "show", "rule", "name=all"], capture_output=True, text=True).stdout
    rules = [line for line in output.splitlines() if any(prefix in line for prefix in RULE_PREFIXES.values())]
    return rules

# GUI Functions

def block_entry():
    ip = ip_entry.get().strip()
    port = port_entry.get().strip()
    proto = proto_var.get()

    if ip:
        rule_name = f"{RULE_PREFIXES['ip']}{ip}"
        subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", "action=block", f"remoteip={ip}"])
        add_to_config(ip, "blocked_ips")

    if port:
        try:
            port_int = int(port)
            rule_name = f"{RULE_PREFIXES['port']}{port}"
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", "action=block", f"localport={port}", "protocol=TCP"])
            add_to_config(port_int, "blocked_ports")
        except ValueError:
            messagebox.showerror("Invalid Port", "Please enter a valid port number.")
            return

    if proto != "":
        rule_name = f"{RULE_PREFIXES['proto']}{proto}"
        subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", "action=block", f"protocol={proto}"])
        add_to_config(proto, "blocked_protocols")

    messagebox.showinfo("Success", "Entries added and blocked successfully.")
    update_rule_list()

def unblock_all():
    if unblock_ip_var.get():
        for ip in load_config().get("blocked_ips", []):
            delete_firewall_rule(f"{RULE_PREFIXES['ip']}{ip}")
        save_config({**load_config(), "blocked_ips": []})

    if unblock_port_var.get():
        for port in load_config().get("blocked_ports", []):
            delete_firewall_rule(f"{RULE_PREFIXES['port']}{port}")
        save_config({**load_config(), "blocked_ports": []})

    if unblock_proto_var.get():
        for proto in load_config().get("blocked_protocols", []):
            delete_firewall_rule(f"{RULE_PREFIXES['proto']}{proto}")
        save_config({**load_config(), "blocked_protocols": []})

    messagebox.showinfo("Unblocked", "Selected rules unblocked.")
    update_rule_list()

def update_rule_list():
    rules_text.delete(1.0, tk.END)
    rules = get_firewall_rules()
    rules_text.insert(tk.END, '\n'.join(rules))

# GUI Setup

root = tk.Tk()
root.title("Advanced Firewall GUI")
root.geometry("700x600")

# Inputs
frame = tk.LabelFrame(root, text="Block Entry")
frame.pack(fill="x", padx=10, pady=5)

tk.Label(frame, text="IP Address").grid(row=0, column=0)
ip_entry = tk.Entry(frame)
ip_entry.grid(row=0, column=1)

tk.Label(frame, text="Port").grid(row=1, column=0)
port_entry = tk.Entry(frame)
port_entry.grid(row=1, column=1)

tk.Label(frame, text="Protocol").grid(row=2, column=0)
proto_var = tk.StringVar()
proto_dropdown = ttk.Combobox(frame, textvariable=proto_var)
proto_dropdown['values'] = ("", "TCP", "UDP", "ICMP")
proto_dropdown.grid(row=2, column=1)

block_btn = tk.Button(frame, text="Block", command=block_entry)
block_btn.grid(row=3, column=1, pady=10)

# Unblock Section
unblock_frame = tk.LabelFrame(root, text="Unblock Options")
unblock_frame.pack(fill="x", padx=10, pady=5)

unblock_ip_var = tk.BooleanVar()
unblock_port_var = tk.BooleanVar()
unblock_proto_var = tk.BooleanVar()

tk.Checkbutton(unblock_frame, text="Unblock All IPs", variable=unblock_ip_var).pack(anchor='w')
tk.Checkbutton(unblock_frame, text="Unblock All Ports", variable=unblock_port_var).pack(anchor='w')
tk.Checkbutton(unblock_frame, text="Unblock All Protocols", variable=unblock_proto_var).pack(anchor='w')

unblock_btn = tk.Button(unblock_frame, text="Unblock Selected", command=unblock_all)
unblock_btn.pack(pady=5)

# Rule Viewer
view_frame = tk.LabelFrame(root, text="Current Firewall Rules")
view_frame.pack(fill="both", expand=True, padx=10, pady=10)

rules_text = tk.Text(view_frame)
rules_text.pack(fill="both", expand=True)

update_btn = tk.Button(root, text="Refresh Rule List", command=update_rule_list)
update_btn.pack(pady=5)

update_rule_list()
root.mainloop()
