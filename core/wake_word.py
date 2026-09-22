import queue
import time
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

class WakeWordDetector:
    def __init__(self, target_word: str = "hey_jarvis", threshold: float = 0.35, device_index: int = 1):
        self.sample_rate = 16000
        self.chunk_size = 1280  # 80ms frames
        self.target_word = target_word
        self.threshold = threshold
        self.device_index = device_index
        self.audio_queue = queue.Queue()

        print(f"[WakeWord] Loading ONNX model on Mic Index {self.device_index}...")
        self.model = Model(wakeword_models=[self.target_word], inference_framework="onnx")

    def _audio_callback(self, indata, frames, time_info, status):
        """Asynchronous audio callback running on hardware audio thread."""
        self.audio_queue.put(indata.copy())

    def wait_for_wake_word(self) -> bool:
        """Listens using an async callback and releases mic immediately on trigger."""
        print(f"\n[Standby] Say 'Hey Jarvis' to wake...")
        self.model.reset()

        # Clear any stale frames from queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        # Start non-blocking stream
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.chunk_size,
            device=self.device_index,
            callback=self._audio_callback
        ):
            while True:
                try:
                    # Non-blocking pull with 1-second timeout
                    audio_frame = self.audio_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                audio_data = audio_frame.flatten()
                prediction = self.model.predict(audio_data)
                score = prediction.get(self.target_word, 0.0)

                if score >= self.threshold:
                    print(f"\n[Triggered] Wake word detected! (Confidence: {score:.2f})")
                    return True