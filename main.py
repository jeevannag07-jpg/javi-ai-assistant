import sys
import time
import winsound
from core.brain import JarvisBrain
from core.voice_out import VoiceOutput
from core.voice_in import VoiceInput
from core.wake_word import WakeWordDetector

def play_chime():
    """Short non-blocking acknowledgement tone."""
    winsound.Beep(1000, 150)

def run():
    print("=" * 65)
    print("  JAVI // STREAMING LOW-LATENCY RUNTIME ONLINE")
    print("  Trigger: 'Hey Jarvis' | Model: Ollama (qwen2.5:3b)")
    print("  Say 'shutdown', 'power down', or 'exit' to stop.")
    print("=" * 65 + "\n")

    speaker = VoiceOutput(rate=195)
    ear = VoiceInput(device_index=1)
    javi = JarvisBrain()
    wake_engine = WakeWordDetector(target_word="hey_jarvis", threshold=0.35, device_index=1)

    boot_line = "Streaming pipeline online. Standing by, Commander."
    print(f"JAVI: {boot_line}\n")
    speaker.speak(boot_line)

    while True:
        try:
            # 1. Passive Standby: Low-CPU callback listener
            wake_engine.wait_for_wake_word()

            # 2. Hardware-safe audio ping
            play_chime()

            # 3. Active Command Capture
            user_command = ear.listen(duration=5)

            if not user_command:
                print("[Standby] No command detected. Resuming standby mode.\n")
                continue

            print(f"\nYou > {user_command}\nJAVI: ", end="", flush=True)

            # 4. Check for shutdown commands
            if any(term in user_command.lower() for term in ["shutdown", "power down", "exit", "quit"]):
                farewell = "Disengaging vocal and operational arrays. Standing by."
                print(farewell)
                speaker.speak(farewell)
                break

            # 5. Stream sentences into speaker in real time
            for sentence in javi.chat_stream(user_command):
                print(f"{sentence} ", end="", flush=True)
                speaker.speak(sentence)

            print("\n")
            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\nJAVI: Core halted via manual override.")
            sys.exit(0)

if __name__ == "__main__":
    run()