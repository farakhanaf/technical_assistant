from flask import Flask, render_template
import psutil
import platform
import socket
import datetime

app = Flask(__name__)

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram_total": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "ram_used": round(psutil.virtual_memory().used / (1024 ** 3), 2),
        "uptime": str(datetime.timedelta(seconds=int(psutil.boot_time()))),
    }

def get_disk_info():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "device": part.device,
                "total": round(usage.total / (1024 ** 3), 2),
                "used": round(usage.used / (1024 ** 3), 2),
                "free": round(usage.free / (1024 ** 3), 2),
            })
        except:
            pass
    return disks

def get_battery_info():
    battery = psutil.sensors_battery()
    if not battery:
        return None
    return {
        "percent": battery.percent,
        "plugged": battery.power_plugged
    }

@app.route("/")
def index():
    return render_template(
        "index.html",
        system=get_system_info(),
        disks=get_disk_info(),
        battery=get_battery_info()
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
