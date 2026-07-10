import os, tinytuya, time
from dotenv import load_dotenv

load_dotenv()

d = tinytuya.OutletDevice(
    dev_id=os.getenv('TUYA_DEVICE_ID', ''),
    address=os.getenv('TUYA_ADDRESS', ''),
    local_key=os.getenv('TUYA_LOCAL_KEY', ''),
    version=float(os.getenv('TUYA_VERSION', '3.5')),
)

print("每5秒刷新一次，按 Ctrl+C 停止")
try:
    while True:
        try:
            d.socket = None
            d.updatedps([18, 19, 20])
            time.sleep(0.3)
            data = d.status()
            dps = data.get('dps', {})
            if not dps:
                print(f"[{time.strftime('%H:%M:%S')}] 無法取得數據")
            else:
                cur_power = int(dps.get('19', 0)) / 10
                cur_current = int(dps.get('18', 0))
                cur_voltage = int(dps.get('20', 0)) / 10
                print(f"[{time.strftime('%H:%M:%S')}] {cur_power:.1f}W  {cur_current}mA  {cur_voltage:.1f}V")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] 錯誤: {e}")
        time.sleep(5)
except KeyboardInterrupt:
    print("\n停止")
