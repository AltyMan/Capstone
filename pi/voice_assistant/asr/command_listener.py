import socket
import json
from pathlib import Path
from vosk import Model, KaldiRecognizer

# Config
HOST = "0.0.0.0"  # Listen on all available interfaces
PORT = 8080
SAMPLE_RATE = 48000  # Expected input: mono, 16-bit PCM, 48kHz
PACKET_SIZE = 4096

SCRIPT_DIR = Path(__file__).resolve().parent
VOSK_MODEL_PATH = SCRIPT_DIR / "models" / "en-us"  # your local Vosk model

vosk_model = Model(str(VOSK_MODEL_PATH))
recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)


def process_audio_stream(conn):
    print("🎧 Listening for speech...")

    while True:
        data = conn.recv(PACKET_SIZE)
        if not data:
            print("Connection closed by client")
            break

        if recognizer.AcceptWaveform(data):
            text = json.loads(recognizer.Result()).get("text", "").strip()
            if text:
                print(f"➡️ Command: {text}")
        else:
            partial = json.loads(recognizer.PartialResult()).get("partial", "").strip()
            if partial:
                print(f"Partial: {partial}")


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
