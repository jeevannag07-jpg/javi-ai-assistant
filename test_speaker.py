from core.voice_out import VoiceOutput

speaker = VoiceOutput(rate=195)
print("Testing utterance 1...")
speaker.speak("First turn: Systems initialized.")

print("Testing utterance 2...")
speaker.speak("Second turn: Running diagnostics.")

print("Testing utterance 3...")
speaker.speak("Third turn: All subsystems fully functional.")
print("Speech test complete.")