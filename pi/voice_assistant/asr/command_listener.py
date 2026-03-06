import socket
import json
from pathlib import Path
from vosk import Model, KaldiRecognizer

# Config
HOST = "0.0.0.0"  # Listen on all available interfaces
PORT = 8080
SAMPLE_RATE = 48000  # Expected input: mono, 16-bit PCM, 48kHz
PACKET_SIZE = 4096
INTENT_HOST = "127.0.0.1"  # intent_handler local server on the same Raspberry Pi
INTENT_PORT = 9090

SCRIPT_DIR = Path(__file__).resolve().parent
VOSK_MODEL_PATH = SCRIPT_DIR / "models" / "en-us"  # your local Vosk model

vosk_model = Model(str(VOSK_MODEL_PATH))


def send_to_intent_handler(text: str) -> None:
    payload = {"text": text}
    try:
        with socket.create_connection((INTENT_HOST, INTENT_PORT), timeout=0.25) as intent_sock:
            intent_sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
    except OSError:
        # Intent service is optional at runtime; listener keeps running if it is down.
        pass


def process_audio_stream(conn):
    print("🎧 Listening for speech...")

    # Create a fresh recognizer for this connection to avoid stale state on reconnects
    recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
    
    # Set a timeout so recv doesn't block forever on disconnect
    conn.settimeout(1.0)

    try:
        while True:
            try:
                data = conn.recv(PACKET_SIZE)
            except socket.timeout:
                print("[INFO] Socket timeout, connection lost")
                break
            
            if not data:
                print("Connection closed by client")
                break

            if recognizer.AcceptWaveform(data):
                text = json.loads(recognizer.Result()).get("text", "").strip()
                if text:
                    print(f"➡️ Command: {text}")
                    send_to_intent_handler(text)
            else:
                partial = json.loads(recognizer.PartialResult()).get("partial", "").strip()
                if partial:
                    print(f"Partial: {partial}")
    except Exception as e:
        print(f"[ERROR] Audio stream processing error: {e}")
    finally:
        print("[INFO] Cleaning up connection...")


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
