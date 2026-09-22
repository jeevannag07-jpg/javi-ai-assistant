import sounddevice as sd
import numpy as np

print("=== AVAILABLE AUDIO INPUT DEVICES ===")
devices = sd.query_devices()
default_in = sd.default.device[0]

for idx, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        is_default = " [DEFAULT]" if idx == default_in else ""
        print(f"Index {idx}: {dev['name']}{is_default}")

print("\n=== RECORDING 3 SECONDS FOR VOLUME CHECK ===")
sample_rate = 16000
duration = 3
print(">>> Speak loudly into your mic now...")
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
sd.wait()

max_vol = np.max(np.abs(audio))
avg_vol = np.mean(np.abs(audio))
print(f"\nMax Volume Detected: {max_vol}")
print(f"Average Volume Detected: {avg_vol}")

if max_vol < 100:
    print("\n[RESULT] ZERO/FLAT AUDIO: Mic is muted, volume is 0, or Windows is blocking access.")
else:
    print("\n[RESULT] AUDIO SIGNAL DETECTED! Mic is working at hardware level.")
