import winsound
import time
from core.wake_word import WakeWordDetector
from core.voice_in import VoiceInput

print("Initializing subsystems...")
wake = WakeWordDetector(target_word="hey_jarvis", threshold=0.40, device_index=1)
ear = VoiceInput(device_index=1)

print("\n--- TEST: SAY 'Hey Jarvis' NOW ---")
wake.wait_for_wake_word()

print("\n[STEP 1] Beeping...")
winsound.Beep(1000, 150)

print("\n[STEP 2] Calling ear.listen(5)...")
cmd = ear.listen(duration=5)

print(f"\n[STEP 3] Finished listening! Received text: '{cmd}'")