import sys
import threading
import time
import winsound
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from core.brain import JarvisBrain
from core.voice_out import VoiceOutput
from core.voice_in import VoiceInput
from core.wake_word import WakeWordDetector

class JaviTrayApp:
    def __init__(self):
        self.running = True
        self.is_muted = False
        self.speaker = VoiceOutput(rate=195)
        self.ear = VoiceInput(device_index=1)
        self.javi = JarvisBrain()
        self.wake_engine = WakeWordDetector(target_word="hey_jarvis", threshold=0.35, device_index=1)
        self.icon = None

    def _create_tray_icon(self):
        """Generates a dynamic 64x64 blue orb icon for the Windows taskbar tray."""
        width, height = 64, 64
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # Outer ring
        draw.ellipse((4, 4, 60, 60), fill=(20, 30, 45), outline=(0, 210, 255), width=3)
        # Inner glowing core
        draw.ellipse((18, 18, 46, 46), fill=(0, 180, 255))
        return image

    def listener_thread(self):
        """Persistent background thread for wake-word spotting and command execution."""
        print("[JAVI Tray] Background engine active.")
        self.speaker.speak("JAVI background runtime active.")

        while self.running:
            try:
                # 1. Background Wake Word Listening
                detected = self.wake_engine.wait_for_wake_word()
                if not self.running:
                    break

                if self.is_muted:
                    continue

                # 2. Audio Beep
                winsound.Beep(1000, 150)

                # 3. Command Capture
                command = self.ear.listen(duration=5)
                if not command:
                    print("[Tray Standby] No audible command recognized.")
                    continue

                print(f"\nYou > {command}\nJAVI: ", end="", flush=True)

                if any(w in command.lower() for w in ["shutdown", "exit", "quit", "power down"]):
                    farewell = "Disengaging system. Standing by."
                    print(farewell)
                    self.speaker.speak(farewell)
                    self.stop_app()
                    break

                # 4. Stream response from LLM + SQLite memory
                for sentence in self.javi.chat_stream(command):
                    print(f"{sentence} ", end="", flush=True)
                    self.speaker.speak(sentence)

                print("\n")
                time.sleep(0.5)

            except Exception as e:
                print(f"[Tray Loop Error] {e}")
                time.sleep(1)

    def toggle_mute(self, icon, item):
        self.is_muted = not self.is_muted
        status = "Muted" if self.is_muted else "Unmuted"
        print(f"[Tray Action] JAVI is now {status}.")

    def stop_app(self, icon=None, item=None):
        print("[Tray Action] Shutting down JAVI cleanly...")
        self.running = False
        if self.icon:
            self.icon.stop()
        sys.exit(0)

    def run(self):
        # Run the voice listener in a background worker thread
        t = threading.Thread(target=self.listener_thread, daemon=True)
        t.start()

        menu = (
            item('Mute / Unmute', self.toggle_mute),
            item('Exit JAVI', self.stop_app),
        )

        image = self._create_tray_icon()
        self.icon = pystray.Icon("JAVI", image, "JAVI Assistant", menu)
        self.icon.run()

if __name__ == "__main__":
    app = JaviTrayApp()
    app.run()