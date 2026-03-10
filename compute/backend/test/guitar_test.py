import pyaudio
import aubio
import numpy as np
from collections import deque

# -----------------------
# CONFIGURATION
# -----------------------
BUFFER_SIZE = 512
HOP_SIZE = 512
SAMPLERATE = 22050        # lower sample rate
SEQUENCE_LENGTH = 3
TOLERANCE_HZ = 40         # allow more pitch variation
STABLE_FRAMES = 3          # number of consecutive frames to confirm note

COMMANDS = {
    ('E4', 'G4', 'A4'): 'COMMAND_1',
    ('A3', 'C4', 'D4'): 'COMMAND_2'
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def freq_to_note(freq):
    if freq <= 0:
        return None
    midi = int(round(69 + 12 * np.log2(freq / 440.0)))
    octave = midi // 12 - 1
    name = NOTE_NAMES[midi % 12]
    return f"{name}{octave}"

# -----------------------
# AUDIO STREAM SETUP
# -----------------------
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLERATE,
                input=True,
                frames_per_buffer=HOP_SIZE)

pitch_o = aubio.pitch("yin", BUFFER_SIZE, HOP_SIZE, SAMPLERATE)
pitch_o.set_unit("Hz")
pitch_o.set_silence(-30)      # higher threshold, ignore quiet sounds

# -----------------------
# MAIN LOOP
# -----------------------
note_buffer = deque(maxlen=SEQUENCE_LENGTH)
stable_count = 0
last_note = None

print("Listening for note sequences... Play your guitar!")

try:
    while True:
        data = stream.read(HOP_SIZE, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.float32)
        freq = pitch_o(samples)[0]
        note = freq_to_note(freq)

        if note:
            # Only consider note stable if it repeats for STABLE_FRAMES
            if note == last_note:
                stable_count += 1
            else:
                stable_count = 1
                last_note = note

            if stable_count >= STABLE_FRAMES:
                if len(note_buffer) == 0 or note_buffer[-1] != note:
                    note_buffer.append(note)
                    print("Detected note:", note)

                # Check for command
                for seq, cmd in COMMANDS.items():
                    if len(note_buffer) == SEQUENCE_LENGTH:
                        # Use tolerance to compare
                        match = all(n1 == n2 for n1, n2 in zip(seq, note_buffer))
                        if match:
                            print(f"Command triggered: {cmd}")
                            note_buffer.clear()

except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()