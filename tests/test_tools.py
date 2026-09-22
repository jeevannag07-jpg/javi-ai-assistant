import os
import platform
import psutil
from typing import Dict, Any

def get_system_diagnostics() -> Dict[str, Any]:
    """
    Fetches real-time system metrics: CPU percentage, RAM utilization,
    and battery status.
    """
    cpu_percent = psutil.cpu_percent(interval=0.2)
    virtual_mem = psutil.virtual_memory()
    battery = psutil.sensors_battery()

    battery_info = "Desktop (AC Power)"
    if battery is not None:
        battery_info = f"{battery.percent}% {'(Charging)' if battery.power_plugged else '(Discharging)'}"

    return {
        "status": "success",
        "cpu_usage": f"{cpu_percent}%",
        "ram_usage": f"{virtual_mem.percent}% ({round(virtual_mem.used / (1024**3), 2)} GB / {round(virtual_mem.total / (1024**3), 2)} GB)",
        "battery": battery_info,
    }

def launch_application(app_name: str) -> Dict[str, str]:
    """
    Launches a desktop application on Windows.
    Common apps: 'notepad', 'calc', 'mspaint', 'chrome'.
    """
    clean_name = app_name.strip().lower()
    os_name = platform.system()

    try:
        if os_name == "Windows":
            os.system(f"start {clean_name}")
            return {"status": "success", "message": f"Launched {clean_name}"}
        elif os_name == "Darwin":
            os.system(f"open -a '{clean_name}'")
            return {"status": "success", "message": f"Launched {clean_name}"}
        else:
            os.system(f"{clean_name} &")
            return {"status": "success", "message": f"Launched {clean_name}"}
    except Exception as exc:
        return {"status": "error", "message": f"Failed to open {clean_name}: {str(exc)}"}

TOOL_REGISTRY = {
    "get_system_diagnostics": get_system_diagnostics,
    "launch_application": launch_application,
}