import socket
import time
import json
import numpy as np
from pathlib import Path
from vosk import Model, KaldiRecognizer
from openwakeword.model import Model as WakeModel

# Config
HOST = "0.0.0.0"  # Listen on all available interfaces
PORT = 8080
SAMPLE_RATE = 48000  # Expected input: mono, 16-bit PCM, 48kHz
PACKET_SIZE = 4096

SCRIPT_DIR = Path(__file__).resolve().parent
VOSK_MODEL_PATH = SCRIPT_DIR / "models" / "en-us"  # your local Vosk model
COMMAND_TIMEOUT = 6  # seconds after wake word to listen for commands
WAKE_THRESHOLD = 0.5  # temporary low threshold for testing (raise later)

print("🔍 Checking for 'hey_jarvis' wake word model...")
# Initialization
wake = WakeModel(wakeword_models=["hey_jarvis"])  # model name only → uses resource directory
print("🎙 OpenWakeWord ready with 'hey_jarvis'")

vosk_model = Model(str(VOSK_MODEL_PATH))
recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)


def process_audio_stream(conn):
    print("🎧 Listening for wake word...")

    listening_for_command = False
    command_start = 0.0
    print_counter = 0

    # Buffer 1 second of float32 audio for wake-word model windows.
    wake_buffer = np.zeros(0, dtype=np.float32)

    while True:
        data = conn.recv(PACKET_SIZE)
        if not data:
            print("Connection closed by client")
            break

        # ESP32 stream is expected to be PCM16 mono.
        pcm16 = np.frombuffer(data, dtype=np.int16)
        if pcm16.size == 0:
            continue

        audio = pcm16.astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        print_counter += 1
        if print_counter % 40 == 0:
            print(f"[net] rms={rms:.6f} samples={len(audio)}")

        wake_buffer = np.concatenate((wake_buffer, audio))

        while wake_buffer.size >= SAMPLE_RATE:
            chunk = wake_buffer[:SAMPLE_RATE]
            wake_buffer = wake_buffer[SAMPLE_RATE:]

            try:
                scores_f32 = wake.predict(chunk)
            except Exception:
                scores_f32 = {}

            try:
                i16 = (np.clip(chunk, -1.0, 1.0) * 32767).astype(np.int16)
                scores_i16 = wake.predict(i16)
            except Exception:
                scores_i16 = {}

            score_name = None
            score_val = 0.0
            for d in (scores_f32, scores_i16):
                for k, v in d.items():
                    v_f = float(v)
                    if v_f > score_val:
                        score_val = v_f
                        score_name = k

            print(
                f"[wake-debug] rms={rms:.4f} best={score_name}:{score_val:.6g} "
                f"f32={scores_f32} i16={scores_i16}"
            )

            if score_name and score_val >= WAKE_THRESHOLD and not listening_for_command:
                print("🟢 Wake word detected!")
                listening_for_command = True
                command_start = time.time()
                wake_buffer = np.zeros(0, dtype=np.float32)
                break

        if listening_for_command:
            if recognizer.AcceptWaveform(pcm16.tobytes()):
                text = json.loads(recognizer.Result()).get("text", "").strip()
                if text:
                    print(f"➡️ Command: {text}")

            if time.time() - command_start > COMMAND_TIMEOUT:
                listening_for_command = False
                print("\n🎧 Listening for wake word...")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Listening for ESP32 audio stream on {HOST}:{PORT}...")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Connected by {addr}")
                process_audio_stream(conn)


if __name__ == "__main__":
    main()
