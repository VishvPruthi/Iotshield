import time
import random

# 🔧 ENVIRONMENT CONFIGURATION (USER ADJUSTABLE)
# NOTE: To make the simulation work instantly, ensure TARGET_BSSID and TARGET_STATION 
# match the placeholder details configured in your frontend Streamlit dashboard (app.py).
TARGET_BSSID = "00:11:22:33:44:55"   # Generic mock Access Point MAC
TARGET_STATION = "AA:BB:CC:DD:EE:FF" # Generic target IoT device MAC (Matches app.py)
WIFI_NAME = "Mock_Smart_Home_Net"    # Generic mock Network SSID

print(f"[*] Simulating live smart home activity surges for {TARGET_STATION}... Press Ctrl+C to stop.")
packet_accumulator = 1000

while True:
    # 1. Idle Phase: Increment packets very slowly (mimics background heartbeat noise)
    print("🟢 Status: System Idle. Sending minimal heartbeats...")
    for _ in range(random.randint(4, 7)):
        packet_accumulator += random.randint(0, 1) # Barely any increase
        with open("live_traffic-01.csv", "w") as f:
            f.write("BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key\n")
            f.write(f"{TARGET_BSSID}B, 2026-09-07 18:53:10, 2026-09-07 18:58:59, 1, 270, WPA2, CCMP, PSK, -35, 3217, 4311, 0.0.0.0, 11, {WIFI_NAME},\n\n")
            f.write("Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs\n")
            f.write(f"{TARGET_STATION}, 2026-09-07 18:53:11, 2026-09-07 18:58:54, -48, {packet_accumulator}, {TARGET_BSSID},\n")
        time.sleep(1)

    # 2. Burst Activity Surge Phase: Aggressively flood packets!
    print("🚨 Status: Human Detected! Camera firing dynamic encrypted macroblocks...")
    for _ in range(5):
        packet_accumulator += random.randint(15, 35) # Massive delta growth!
        with open("live_traffic-01.csv", "w") as f:
            f.write("BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key\n")
            f.write(f"{TARGET_BSSID}B, 2026-09-07 18:53:10, 2026-09-07 18:58:59, 1, 270, WPA2, CCMP, PSK, -35, 3217, 4311, 0.0.0.0, 11, {WIFI_NAME},\n\n")
            f.write("Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs\n")
            f.write(f"{TARGET_STATION}, 2026-09-07 18:53:11, 2026-09-07 18:58:54, -48, {packet_accumulator}, {TARGET_BSSID},\n")
        time.sleep(1)
