import os, time, threading
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge
import tinytuya

load_dotenv()

DEV_ID = os.getenv('TUYA_DEVICE_ID', '')
ADDRESS = os.getenv('TUYA_ADDRESS', '')
LOCAL_KEY = os.getenv('TUYA_LOCAL_KEY', '')
VERSION = float(os.getenv('TUYA_VERSION', '3.5'))
INTERVAL = int(os.getenv('TUYA_POLL_INTERVAL', '5'))
PORT = int(os.getenv('EXPORTER_PORT', '8000'))
DEVICE_NAME = os.getenv('DEVICE_NAME', 'Smart plug')

label_keys = ('device_id', 'device_name')
labels = {'device_id': DEV_ID, 'device_name': DEVICE_NAME}

power_g = Gauge('tuya_power_watts', '即時功率', label_keys)
current_g = Gauge('tuya_current_amperes', '即時電流', label_keys)
voltage_g = Gauge('tuya_voltage', '即時電壓', label_keys)

d = tinytuya.OutletDevice(dev_id=DEV_ID, address=ADDRESS,
                          local_key=LOCAL_KEY, version=VERSION)

def poll():
    while True:
        try:
            d.socket = None
            d.updatedps([18, 19, 20])
            time.sleep(0.3)
            data = d.status()
            dps = data.get('dps', {})
            if dps:
                pw = int(dps.get('19', 0)) / 10
                ca = int(dps.get('18', 0)) / 1000
                vo = int(dps.get('20', 0)) / 10
                power_g.labels(**labels).set(pw)
                current_g.labels(**labels).set(ca)
                voltage_g.labels(**labels).set(vo)
        except Exception as e:
            print(f"poll error: {e}")
        time.sleep(INTERVAL)

threading.Thread(target=poll, daemon=True).start()
start_http_server(PORT)
print(f"Exporter running on :{PORT}/metrics")
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("\n停止")
