import requests
from flask import Blueprint, request, jsonify
from objects.user import User

mqtt_bp = Blueprint('mqtt', __name__)

import subprocess

def speak(text):
    subprocess.run([
        "piper",
        "--model", "C:\\Users\\Owner\\Documents\\Dev\\Capstone\\compute\\backend\\routes\\en_US-lessac-high.onnx",
        "--output_file", "out.wav"
    ], input=text.encode())

    subprocess.run([
        "powershell",
        "-c",
        '(New-Object Media.SoundPlayer "out.wav").PlaySync();'
    ])

GATEWAY_URL = "https://raspberrypi.tailbe7155.ts.net"

@mqtt_bp.get("/health")
def health():
    res = requests.get(f"{GATEWAY_URL}/health")
    return jsonify(res.json()), res.status_code

@mqtt_bp.get("/devices")
def get_devices():
    res = requests.get(f"{GATEWAY_URL}/devices")
    return jsonify(res.json()), res.status_code

@mqtt_bp.get("/devices/<device_id>")
def get_device(device_id: str):
    res = requests.get(f"{GATEWAY_URL}/devices/{device_id}")
    return jsonify(res.json()), res.status_code

@mqtt_bp.post("/devices/<device_id>/set")
def set_device(device_id: str):
    state = request.args.get("state")

    if state is None:
        return jsonify({"error": "Missing 'state' query parameter"}), 400

    res = requests.post(
        f"{GATEWAY_URL}/devices/{device_id}/set",
        json={
            "state": state,
            "user_id": "1",
            "source": "1",
        },    
    )

    user = User(1)

    user_habits = user.get_habits()
    user_habit_names = [h.habit_name for h in user_habits]
    if device_id in user_habit_names:
        user.log_habit(state=state, self_reported=True, habit_name=device_id)
    
    # speak(f"{device_id} is {state} vro")

    return jsonify(res.json()), res.status_code
