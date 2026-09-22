import os
import io
import base64
import ctypes
import datetime
import psutil
from typing import Dict, Any
from PIL import ImageGrab
import ollama
from duckduckgo_search import DDGS
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Windows Virtual-Key codes for media control
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP       = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002

def _get_volume_endpoint():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return interface.QueryInterface(IAudioEndpointVolume)

def set_system_volume(level: int) -> Dict[str, Any]:
    try:
        volume = _get_volume_endpoint()
        clamped_level = max(0, min(100, int(level)))
        volume.SetMasterVolumeLevelScalar(clamped_level / 100.0, None)
        return {"status": "success", "message": f"Master volume set to {clamped_level}%"}
    except Exception as exc:
        return {"status": "error", "message": f"Failed to set volume: {str(exc)}"}

def toggle_mute() -> Dict[str, Any]:
    try:
        volume = _get_volume_endpoint()
        current_mute = volume.GetMute()
        new_state = not current_mute
        volume.SetMute(new_state, None)
        state_str = "muted" if new_state else "unmuted"
        return {"status": "success", "message": f"Audio is now {state_str}"}
    except Exception as exc:
        return {"status": "error", "message": f"Failed to toggle mute: {str(exc)}"}

def control_media(action: str) -> Dict[str, Any]:
    action_clean = action.strip().lower()
    key_map = {
        "play_pause": VK_MEDIA_PLAY_PAUSE,
        "play": VK_MEDIA_PLAY_PAUSE,
        "pause": VK_MEDIA_PLAY_PAUSE,
        "next": VK_MEDIA_NEXT_TRACK,
        "previous": VK_MEDIA_PREV_TRACK,
        "prev": VK_MEDIA_PREV_TRACK,
        "stop": VK_MEDIA_STOP,
    }

    if action_clean not in key_map:
        return {"status": "error", "message": f"Unsupported action: {action}"}

    vk_code = key_map[action_clean]
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
    return {"status": "success", "message": f"Executed media command: {action_clean}"}

def get_system_diagnostics() -> Dict[str, Any]:
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
    clean_name = app_name.strip().lower()
    try:
        os.system(f"start {clean_name}")
        return {"status": "success", "message": f"Launched {clean_name}"}
    except Exception as exc:
        return {"status": "error", "message": f"Failed to open {clean_name}: {str(exc)}"}

def search_web(query: str) -> Dict[str, Any]:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return {"status": "empty", "message": "No search results found."}
            snippets = [f"{r['title']}: {r['body']}" for r in results]
            return {"status": "success", "results": " | ".join(snippets)}
    except Exception as exc:
        return {"status": "error", "message": f"Web search failed: {str(exc)}"}

def get_daily_briefing() -> Dict[str, Any]:
    """Generates an executive daily briefing with local time, date, weather snapshot, and battery level."""
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p")

    # System vitals
    battery = psutil.sensors_battery()
    bat_str = f"{battery.percent}%" if battery else "AC Power"

    # Quick weather lookup
    weather_summary = "Weather data unavailable"
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text("current local weather today temperature conditions", max_results=1))
            if res:
                weather_summary = res[0]['body']
    except Exception:
        pass

    return {
        "status": "success",
        "date": date_str,
        "time": time_str,
        "battery": bat_str,
        "weather_snapshot": weather_summary
    }

def analyze_screen(prompt: str = "Describe and analyze what is on this screen in 1 or 2 concise sentences.") -> Dict[str, Any]:
    """Captures the current primary display and evaluates it using a local multimodal vision model."""
    try:
        screenshot = ImageGrab.grab()
        # Downscale image to 1024px width for rapid local vision inference
        screenshot.thumbnail((1024, 1024))
        
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG", quality=80)
        img_bytes = buffer.getvalue()

        # Run inference via local Ollama vision model
        res = ollama.chat(
            model="llava:7b",
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [img_bytes]
            }]
        )
        analysis = res["message"]["content"]
        return {"status": "success", "screen_analysis": analysis}
    except Exception as exc:
        return {"status": "error", "message": f"Vision analysis failed: {str(exc)}"}

TOOL_REGISTRY = {
    "get_system_diagnostics": get_system_diagnostics,
    "launch_application": launch_application,
    "search_web": search_web,
    "set_system_volume": set_system_volume,
    "toggle_mute": toggle_mute,
    "control_media": control_media,
    "get_daily_briefing": get_daily_briefing,
    "analyze_screen": analyze_screen,
}