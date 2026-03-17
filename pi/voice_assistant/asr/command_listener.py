import socket
import json
from pathlib import Path
from vosk import Model, KaldiRecognizer
from tts_helper import generate_tts_mp3 

# Config
HOST = "0.0.0.0" 
PORT = 8080
SAMPLE_RATE = 16000 
PACKET_SIZE = 4096
INTENT_HOST = "127.0.0.1" 
INTENT_PORT = 9090

SCRIPT_DIR = Path(__file__).resolve().parent
VOSK_MODEL_PATH = SCRIPT_DIR / "models" / "en-us"

vosk_model = Model(str(VOSK_MODEL_PATH))

def send_to_intent_handler(text: str) -> str:
    payload = {"text": text}
    try:
        with socket.create_connection((INTENT_HOST, INTENT_PORT), timeout=2.0) as intent_sock:
            intent_sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            response = intent_sock.recv(4096)
            return response.decode('utf-8').strip()
    except OSError:
        return "The intent service is currently offline."
    return "I couldn't process that request."

def process_audio_stream(conn, recognizer):
    print("🎧 Listening for speech...")
    
    conn.settimeout(1.5)
    final_text = ""

    try:
        while True:
            try:
                data = conn.recv(PACKET_SIZE)
            except socket.timeout:
                print("[INFO] ESP32 5-second audio stream finished.")
                break 
            
            if not data:
                break

            if recognizer.AcceptWaveform(data):
                text = json.loads(recognizer.Result()).get("text", "").strip()
                if text:
                    final_text += text + " "

        res = json.loads(recognizer.FinalResult())
        text = res.get("text", "").strip()
        if text:
            final_text += text + " "
            
        final_text = final_text.strip()
        
        # Ask Intent Handler or Fallback to Error File
        if final_text:
            print(f"➡️ Command: {final_text}")
            response_files = send_to_intent_handler(final_text)
        else:
            response_files = "i-m-sorry-i-didn-t-understand-that-command.mp3"
            
        print(f"💬 MP3s queued to play: {response_files}")
        
        # Get local MP3 bytes
        mp3_bytes = generate_tts_mp3(response_files)
        
        # Send MP3 to ESP32
        if mp3_bytes:
            print("[INFO] Pushing MP3 audio back to ESP32...")
            conn.sendall(mp3_bytes)

    except Exception as e:
        print(f"[ERROR] Audio stream processing error: {e}")
    finally:
        print("[INFO] Closing socket. ESP32 will now play the MP3.")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Listening for ESP32 audio stream on {HOST}:{PORT}...")

        while True:
            # THE FIX: Pre-load the STT graph while idling! 
            # This costs 0 latency when the connection actually happens.
            recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
            
            conn, addr = server.accept()
            with conn:
                print(f"Connected by {addr}")
                # Pass the perfectly prepped recognizer directly in
                process_audio_stream(conn, recognizer)

if __name__ == "__main__":
    main()