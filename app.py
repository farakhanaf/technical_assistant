from flask import Flask, render_template, jsonify
import psutil
import platform
import socket
import datetime
import getpass
import time

app = Flask(__name__)

def get_system_info():
    uptime_seconds = int(time.time() - psutil.boot_time())

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
        "uptime": str(datetime.timedelta(seconds=uptime_seconds)),
        "current_user": getpass.getuser(),
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

def get_system_health():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    return {
        "current_user": getpass.getuser(),
        "uptime": str(datetime.timedelta(seconds=uptime_seconds)),
        "load": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None
    }

def get_cpu_detail():
    freq = psutil.cpu_freq()
    return {
        "usage_total": psutil.cpu_percent(interval=1),
        "usage_per_core": psutil.cpu_percent(interval=1, percpu=True),
        "frequency_current": freq.current if freq else None,
        "frequency_max": freq.max if freq else None
    }

def get_memory_detail():
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "ram_total": round(vm.total / 1e9, 2),
        "ram_used": round(vm.used / 1e9, 2),
        "ram_available": round(vm.available / 1e9, 2),
        "ram_percent": vm.percent,
        "swap_used": round(swap.used / 1e9, 2),
        "swap_percent": swap.percent
    }

def get_disk_io():
    io = psutil.disk_io_counters()
    return {
        "read_gb": round(io.read_bytes / 1e9, 2),
        "write_gb": round(io.write_bytes / 1e9, 2)
    }

def get_top_processes(limit=5):
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(p.info)

    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:limit]

def get_network_info():
    net = psutil.net_io_counters()
    return {
        "bytes_sent_mb": round(net.bytes_sent / 1e6, 2),
        "bytes_recv_mb": round(net.bytes_recv / 1e6, 2)
    }

def get_battery_detail():
    b = psutil.sensors_battery()
    if not b:
        return None
    return {
        "percent": b.percent,
        "plugged": b.power_plugged,
        "time_left": str(datetime.timedelta(seconds=b.secsleft)) if b.secsleft > 0 else "Unknown"
    }

@app.route("/")
def index():
    return render_template(
        "index.html",
        system=get_system_info(),
        cpu=get_cpu_detail(),
        memory=get_memory_detail(),
        disks=get_disk_info(),
        disk_io=get_disk_io(),
        network=get_network_info(),
        battery=get_battery_detail(),
        processes=get_top_processes()
    )

@app.route("/api/status")
def api_status():
    return jsonify({
        "system": get_system_info(),
        "cpu": get_cpu_detail(),
        "memory": get_memory_detail(),
        "disk_io": get_disk_io(),
        "network": get_network_info(),
        "battery": get_battery_detail(),
        "processes": get_top_processes()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
