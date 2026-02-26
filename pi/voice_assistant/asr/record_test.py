import socket
import wave
import sys

HOST = '0.0.0.0'
PORT = 8080
SAMPLE_RATE = 16000  # LyraT Mini audio codec native rate (48kHz)
CHANNELS = 1         # Stereo
SAMPLE_WIDTH = 2     # 16 bits = 2 bytes
CHUNK_SIZE = 4096

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening for ESP32 {SAMPLE_RATE}Hz audio stream on port {PORT}...")
    print(f"Configuration: {CHANNELS} channels, {SAMPLE_WIDTH} bytes per sample (16-bit)")
    
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        
        wf = wave.open("debug_raw_audio.wav", "wb")
        wf.setnchannels(CHANNELS)     
        wf.setsampwidth(SAMPLE_WIDTH)     
        wf.setframerate(SAMPLE_RATE)
        
        bytes_received = 0
        frames_received = 0
        
        try:
            while True:
                data = conn.recv(CHUNK_SIZE)
                if not data:
                    print("Connection closed by ESP32")
                    break
                bytes_received += len(data)
                frames_received += 1
                wf.writeframes(data)
                print(f"Frame {frames_received}: {len(data)} bytes (total: {bytes_received} bytes)")
                        
        except KeyboardInterrupt:
            print("\nStopping and saving audio...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            wf.close()
            print(f"debug_raw_audio.wav saved. Total received: {bytes_received} bytes in {frames_received} frames")