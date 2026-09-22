import pyttsx3

class VoiceOutput:
    def __init__(self, rate: int = 195):
        self.rate = rate

    def speak(self, text: str):
        """
        Initializes a fresh SAPI5 engine instance per call to prevent
        the Windows COM event loop from freezing on subsequent turns.
        """
        if not text:
            return
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            
            # Select system default voice
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[Speech Synthesis Error] {e}")
