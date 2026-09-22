import io
import time
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import speech_recognition as sr

class VoiceInput:
    def __init__(self, sample_rate: int = 16000, device_index: int = 1):
        self.sample_rate = sample_rate
        self.device_index = device_index
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = False

    def calibrate(self):
        try:
            device_info = sd.query_devices(self.device_index)
            print(f"[Audio In] Bound to: {device_info['name']}")
        except Exception as e:
            print(f"[Audio Warning] {e}")

    def listen(self, duration: int = 5) -> str:
        """Records from AMD mic, verifies volume, and transcribes."""
        time.sleep(0.15)
        print(f"\n[Listening] Speak your command now ({duration}s)...")
        try:
            audio_array = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                device=self.device_index
            )
            sd.wait()

            max_vol = np.max(np.abs(audio_array))
            if max_vol < 400:
                return ""

            wav_buffer = io.BytesIO()
            wavfile.write(wav_buffer, self.sample_rate, audio_array)
            wav_buffer.seek(0)

            with sr.AudioFile(wav_buffer) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text.strip()

        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[STT Error] {e}")
            return ""