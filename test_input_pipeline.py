from core.wake_word import WakeWordDetector
from core.voice_in import VoiceInput

print("=== STEP 1: TESTING WAKE WORD DETECTION ===")
wake = WakeWordDetector(target_word="javi", device_index=1)
print("Say 'Javi' or 'Hey Javi' clearly into your microphone...")
detected = wake.wait_for_wake_word(chunk_duration=2)

if detected:
    print("\n>>> Wake word SUCCESS! Detected. <<<\n")

print("=== STEP 2: TESTING COMMAND CAPTURE (5 SECONDS) ===")
ear = VoiceInput(device_index=1)
ear.calibrate()
print("Speak a full sentence (e.g., 'What is my battery level?')...")
command = ear.listen(duration=5)

print(f"\n--> Recognized Command: '{command}'")
if not command:
    print("[FAIL] No command text transcribed.")
else:
    print("[SUCCESS] Audio pipeline fully functioning.")