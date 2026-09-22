import numpy as np
import sounddevice as sd
from openwakeword.model import Model

print("Loading ONNX model...")
model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

sample_rate = 16000
chunk_size = 1280  # 80ms frames

print("\n=== LIVE AUDIO & CONFIDENCE MONITOR ===")
print("Speak 'Hey Jarvis' or 'Javi' into your microphone now.\n")

with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', blocksize=chunk_size, device=1) as stream:
    count = 0
    while True:
        try:
            audio_frame, _ = stream.read(chunk_size)
            audio_data = audio_frame.flatten()
            
            # Predict
            prediction = model.predict(audio_data)
            score = prediction.get("hey_jarvis", 0.0)
            vol = np.max(np.abs(audio_data))

            count += 1
            # Print every ~240ms (every 3 frames)
            if count % 3 == 0:
                bar = "#" * int(score * 20)
                print(f"\rVol: {vol:5d} | Score: {score:.3f} | [{bar:<20}]", end="", flush=True)

            if score >= 0.35:
                print(f"\n\n>>> TRIGGERED! Wake score reached {score:.3f} <<<")
                break

        except KeyboardInterrupt:
            print("\nStopped.")
            break