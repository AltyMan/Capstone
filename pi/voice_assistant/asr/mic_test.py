import sounddevice as sd
import numpy as np
import wave
from pathlib import Path

OUT = Path(__file__).resolve().parent / "mic_test.wav"
SR = 16000
DUR = 5.0
CH = 1

print("Recording", DUR, "s at", SR, "Hz...")
rec = sd.rec(int(DUR * SR), samplerate=SR, channels=CH, dtype='float32')
sd.wait()
arr = rec.flatten()
rms = float((arr.astype('float64')**2).mean()**0.5)
print("Recorded RMS:", rms)

# convert to int16 and write WAV
pcm = (arr * 32767).astype('<i2').tobytes()
with wave.open(str(OUT), 'wb') as wf:
    wf.setnchannels(CH)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm)

print("WAV written to", OUT)