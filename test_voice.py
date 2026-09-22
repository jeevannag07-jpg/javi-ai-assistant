from core.voice_in import VoiceInput

def main():
    ear = VoiceInput(device_index=1)
    ear.calibrate()
    print("Test ready. Speak a short sentence when prompted.")
    text = ear.listen(duration=4)
    print(f"\n--> Recognized Output: '{text}'")

if __name__ == "__main__":
    main()