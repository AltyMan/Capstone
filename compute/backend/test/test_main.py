import queue
import sounddevice as sd
import vosk
import json
import requests


MODEL_PATH = "C:\\Users\\Owner\\Documents\\Dev\\Capstone\\compute\\backend\\test\\vosk-model-small-en-us-0.15_c_\\vosk-model-small-en-us-0.15"

SERVER = "http://192.168.2.158:5000"

q = queue.Queue()

commands = [
    "turn on plug one",
    "turn off plug one",
    "turn on plug two",
    "turn off plug two",
    "turn on plug three",
    "turn off plug three"
]

plug_map = {
    "one": "plug1",
    "two": "plug2",
    "three": "plug3"
}

def audio_callback(indata, frames, time, status):
    q.put(bytes(indata))

def send_command(device, state):
    url = f"{SERVER}/devices/{device}/set?state={state}"
    r = requests.post(url)
    print("Request:", url)
    print("Status:", r.status_code)

def parse_command(text):
    words = text.split()

    state = None
    plug = None

    if "on" in words:
        state = "on"
    elif "off" in words:
        state = "off"

    for w in words:
        if w in plug_map:
            plug = plug_map[w]

    if state and plug:
        return plug, state

    return None, None

def main():
    model = vosk.Model(MODEL_PATH)

    rec = vosk.KaldiRecognizer(
        model,
        16000,
        json.dumps(commands)
    )

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        print("Listening...")

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")

                if text:
                    print("Heard:", text)

                    plug, state = parse_command(text)

                    if plug and state:
                        send_command(plug, state)

if __name__ == "__main__":
    main()