import socket
import sys
from vosk import Model, KaldiRecognizer
from pathlib import Path

# Configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 8080
SAMPLE_RATE = 48000

SCRIPT_DIR = Path(__file__).resolve().parent
VOSK_MODEL_PATH = SCRIPT_DIR / "models" / "en-us"   # your local Vosk model

# Initialize Vosk (Download a model from alphacephei.com/vosk/models and extract it)
# Example: model = Model("vosk-model-small-en-us-0.15")
model = Model(str(VOSK_MODEL_PATH))
rec = KaldiRecognizer(model, SAMPLE_RATE)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening for ESP32 audio stream on port {PORT}...")
    
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(4096)
            if not data:
                break
            
            # Feed raw audio data directly into Vosk
            if rec.AcceptWaveform(data):
                print("Result:", rec.Result())
            else:
                partial = rec.PartialResult()
                if len(partial) > 14: # Filter out empty partials
                    print("Partial:", partial)