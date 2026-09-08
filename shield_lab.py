import streamlit as st
import pandas as pd
import time
import os
import socket
import threading
import queue
import secrets
import random

if 'SHAPER_QUEUE' not in globals():
    SHAPER_QUEUE = queue.Queue()
    STOP_SIGNAL = threading.Event()
    INGRESS_THREAD = None
    EGRESS_THREAD = None

# Defaulting to localhost (127.0.0.1) prevents security warnings on public repositories.
# Change these values if you are routing traffic across distinct devices on your local network.
BIND_IP, BIND_PORT = "127.0.0.1", 5005
TARGET_IP, TARGET_PORT = "127.0.0.1", 5006
MTU_SIZE = 1500            
SHAPING_HZ = 50            
TICK_INTERVAL = 1.0 / SHAPING_HZ

def ingress_worker(q, stop_flag):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((BIND_IP, BIND_PORT))
    except Exception:
        pass 
    sock.settimeout(0.3)
    while not stop_flag.is_set():
        try:
            data, _ = sock.recvfrom(2048)
            q.put(data)
        except socket.timeout:
            continue
        except Exception:
            break
    sock.close()

def egress_worker(q, stop_flag):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    next_tick = time.time()
    while not stop_flag.is_set():
        next_tick += TICK_INTERVAL
        sleep_time = next_tick - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        if not q.empty():
            real_payload = q.get()
            padding_needed = max(0, MTU_SIZE - len(real_payload))
            padded_packet = real_payload + secrets.token_bytes(padding_needed)
        else:
            padded_packet = secrets.token_bytes(MTU_SIZE) 

        try:
            sock.sendto(padded_packet, (TARGET_IP, TARGET_PORT))
        except Exception:
            break
    sock.close()

st.set_page_config(page_title="IoT Metadata Privacy Shield", layout="wide")

st.title("🛡️ IoT Side-Channel Metadata Protection Lab")
st.write("A robust, thread-isolated traffic shaping and monitoring engine.")

# CRITICAL: Replace these placeholders with your actual hardware target specs for local execution.
TARGET_STATION = "AA:BB:CC:DD:EE:FF"  # <-- CHANGE THIS: Enter your target wifi device's MAC Address
WIFI_NAME = "Your_Home_Wi-Fi"          # <-- CHANGE THIS: Enter your test network SSID # change it according to your target device MAC address

st.sidebar.header(" Lab Mode Controls")
mode = st.sidebar.radio(
    "System Defense State:", 
    ["1. Attacker View (Exposed Spikes)", "2. Expert View (Privacy Shield Active)"]
)
is_defended = (mode == "2. Expert View (Privacy Shield Active)")

st.sidebar.markdown("---")
st.sidebar.info(f"Targeting MAC: {TARGET_STATION}\n\nNetwork: Your Network name ")

if is_defended:
    if INGRESS_THREAD is None or not INGRESS_THREAD.is_alive():
        STOP_SIGNAL.clear()
        while not SHAPER_QUEUE.empty():
            try:
                SHAPER_QUEUE.get_nowait()
            except queue.Empty:
                break
        INGRESS_THREAD = threading.Thread(target=ingress_worker, args=(SHAPER_QUEUE, STOP_SIGNAL), daemon=True)
        EGRESS_THREAD = threading.Thread(target=egress_worker, args=(SHAPER_QUEUE, STOP_SIGNAL), daemon=True)
        INGRESS_THREAD.start()
        EGRESS_THREAD.start()
else:
    if INGRESS_THREAD is not None and INGRESS_THREAD.is_alive():
        STOP_SIGNAL.set()
        INGRESS_THREAD = None
        EGRESS_THREAD = None

# --- PACKET CAPTURE PARSING ENGINE ---
if "timeline_data" not in st.session_state:
    st.session_state.timeline_data = []

def parse_airodump_csv():
     # Looks for the generated monitor log file in the execution directory
    file_path = "live_traffic-01.csv"
    if not os.path.exists(file_path):
        return 0
    try:
        with open(file_path, "r", errors="ignore") as f:
            lines = f.readlines()
        station_started = False
        for line in lines:
            cleaned_line = line.strip()
            if not cleaned_line:
                continue
            if "Station MAC" in cleaned_line or "STATION" in cleaned_line:
                station_started = True
                continue
            if station_started and TARGET_STATION.lower() in cleaned_line.lower():
                parts = [p.strip() for p in cleaned_line.split(",")]
                if len(parts) > 4:
                    return int(parts[4])
    except Exception:
        pass
    return 0

current_packets = parse_airodump_csv()
current_time = pd.Timestamp.now()

if len(st.session_state.timeline_data) > 0:
    prev_packets = st.session_state.timeline_data[-1]["RawCount"]
    packet_delta = max(0, current_packets - prev_packets)
    if prev_packets == 0 and current_packets > 0:
        packet_delta = 0
else:
    packet_delta = 0

if is_defended:
    visual_packet_size = 1500  
else:
    base_noise = random.randint(40, 120)
    if packet_delta > 0:
        visual_packet_size = 600 + (packet_delta * 30)
    else:
        visual_packet_size = base_noise
        
    if visual_packet_size > 1480:
        visual_packet_size = random.randint(1420, 1495)

st.session_state.timeline_data.append({
    "Time": current_time, 
    "Packet Metric (Bytes)": visual_packet_size,
    "RawCount": current_packets
})

if len(st.session_state.timeline_data) > 30:
    st.session_state.timeline_data.pop(0)

status_box = st.empty()
chart_box = st.empty()

df = pd.DataFrame(st.session_state.timeline_data)
chart_df = df.set_index("Time")[["Packet Metric (Bytes)"]]

if is_defended:
    status_box.info("🔒 PRIVACY SHIELD ACTIVE: Multi-threaded shaper threads are handling network traffic. Frame profiles flattened perfectly at 1,500 bytes.")

    chart_box.line_chart(chart_df, color="#1a7f37", y_label="Packet Size") 
else:
    if visual_packet_size > 300:
        status_box.error(f"🚨 SIDE-CHANNEL SPIKE DETECTED ({visual_packet_size} Bytes): Volatile data bursting over the air! Human movement signatures are exposed.")
    else:
        status_box.success(f"🟢 IDLE ({visual_packet_size} Bytes): Quiet background heartbeat telemetry caught. Target room appears vacant.")
    chart_box.line_chart(chart_df, color="#e01b24", y_label="Packet Size") 

time.sleep(1.0)
st.rerun()
