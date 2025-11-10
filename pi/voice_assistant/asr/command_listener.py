import sounddevice as sd
import queue, time, json
import numpy as np
from pathlib import Path
from vosk import Model, KaldiRecognizer
from openwakeword.model import Model as WakeModel
from openwakeword.utils import download_models
import wave, sys

# Diagnostics
print("SoundDevice default.device:", sd.default.device)
print("SoundDevice default.samplerate:", sd.default.samplerate)
try:
    print("Available devices (brief):")
    for i, d in enumerate(sd.query_devices()):
        print(f"  {i}: {d['name']} (max_in:{d['max_input_channels']}, default_samplerate:{d['default_samplerate']})")
except Exception as e:
    print("Could not query devices:", e)

# Config
SCRIPT_DIR = Path(__file__).resolve().parent
VOSK_MODEL_PATH = SCRIPT_DIR / "models" / "en-us"   # your local Vosk model
COMMAND_TIMEOUT = 6  # seconds after wake word to listen for commands

print("🔍 Checking for 'hey_jarvis' wake word model...")
download_models(model_names=["hey_jarvis"])  # downloads to openwakeword's internal resources if missing

# Initialization
wake = WakeModel(wakeword_models=["hey_jarvis"])  # model name only → uses resource directory
print("🎙 OpenWakeWord ready with 'hey_jarvis'")

vosk_model = Model(str(VOSK_MODEL_PATH))
recognizer = KaldiRecognizer(vosk_model, 16000)
audio_queue = queue.Queue()

# Audio callback
_print_counter = 0
def audio_callback(indata, frames, time_info, status):
    global _print_counter
    if status:
        print("Audio status:", status)
    # RawInputStream returns bytes, InputStream returns numpy array. Handle both.
    if isinstance(indata, np.ndarray):
        arr = indata.copy()
    else:
        arr = np.frombuffer(indata, dtype=np.float32).reshape(-1, 1)
    arr = arr.flatten()
    # compute RMS to see if mic is hearing anything
    rms = float(np.sqrt(np.mean(arr.astype(np.float64) ** 2)))
    _print_counter += 1
    if _print_counter % 40 == 0:  # throttle prints
        print(f"[mic] rms={rms:.6f} len={len(arr)}")
    audio_queue.put((arr, rms))


# Main loop
def main():
    print("🎧 Listening for wake word...")

    listening_for_command = False
    command_start = 0

    # Use explicit samplerate and mono channels. If your device supports different samplerate, change here.
    SR = 16000
    # buffer 1 second of audio before calling the wake model
    buf = np.zeros(0, dtype=np.float32)
    WAKE_THRESHOLD = 0.5  # temporary low threshold for testing (raise later)

    with sd.RawInputStream(samplerate=SR, blocksize=512, dtype='float32', channels=1, callback=audio_callback):
        while True:
            audio, rms = audio_queue.get()
            # append incoming frame(s) to buffer
            buf = np.concatenate((buf, audio.astype(np.float32)))
            # process every full second (or change to model's expected window)
            while buf.size >= SR:
                chunk = buf[:SR]
                buf = buf[SR:]
                # try predict on float32 normalized input and on int16-scaled input
                try:
                    scores_f32 = wake.predict(chunk)
                except Exception as e:
                    scores_f32 = {}
                try:
                    i16 = (np.clip(chunk, -1.0, 1.0) * 32767).astype(np.int16)
                    scores_i16 = wake.predict(i16)
                except Exception as e:
                    scores_i16 = {}

                # show diagnostics: use the larger score of the two formats for decision
                score_name = None
                score_val = 0.0
                for d in (scores_f32, scores_i16):
                    for k, v in d.items():
                        v_f = float(v)
                        if v_f > score_val:
                            score_val = v_f
                            score_name = k

                print(f"[wake-debug] rms={rms:.4f} best={score_name}:{score_val:.6g} f32={scores_f32} i16={scores_i16}")

                # detection (use whichever format gave best score)
                if score_name and score_val >= WAKE_THRESHOLD and not listening_for_command:
                    print("🟢 Wake word detected!")
                    listening_for_command = True
                    command_start = time.time()
                    # optionally flush buf so command audio is fresh
                    buf = np.zeros(0, dtype=np.float32)
                    break

            # Command recognition (same as before)
            if listening_for_command:
                # feed short frames to Vosk; ensure you pass int16 PCM
                vosk_audio = (audio * 32767).astype(np.int16).tobytes()
                if recognizer.AcceptWaveform(vosk_audio):
                    text = json.loads(recognizer.Result()).get("text", "").strip()
                    if text:
                        print(f"➡️ Command: {text}")

                if time.time() - command_start > COMMAND_TIMEOUT:
                    listening_for_command = False
                    print("\n🎧 Listening for wake word...")


if __name__ == "__main__":
    main()
