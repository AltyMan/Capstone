import json
import time
import threading
from typing import Any, Dict, Optional

import yaml
import paho.mqtt.client as mqtt

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883
REGISTRY_PATH = "/home/capstone/devices.yaml"


def std_set_topic(device_id: str) -> str:
    return f"/home/{device_id}/set"


def std_status_topic(device_id: str) -> str:
    return f"/home/{device_id}/status"


def now_ts() -> int:
    return int(time.time())


def parse_standard_command(payload: bytes) -> Optional[str]:
    text = payload.decode(errors="replace").strip()
    low = text.lower()

    if low in ("on", "off", "toggle"):
        return low
    if low in ("1", "true"):
        return "on"
    if low in ("0", "false"):
        return "off"

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    state = str(data.get("state", "")).strip().lower()
    if state in ("on", "off", "toggle"):
        return state
    if state in ("1", "true"):
        return "on"
    if state in ("0", "false"):
        return "off"

    return None


def parse_vendor_state(payload: bytes) -> Optional[str]:
    text = payload.decode(errors="replace").strip()
    low = text.lower()

    if low in ("on", "off"):
        return low.upper()
    if text in ("ON", "OFF"):
        return text

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if isinstance(data.get("output"), bool):
        return "ON" if data["output"] else "OFF"
    if isinstance(data.get("on"), bool):
        return "ON" if data["on"] else "OFF"
    if isinstance(data.get("state"), str):
        s = data["state"].strip().lower()
        if s in ("on", "off"):
            return s.upper()

    return None


def load_registry(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "devices" not in data:
        raise RuntimeError("devices.yaml must contain top-level key: devices")

    if not isinstance(data["devices"], dict) or not data["devices"]:
        raise RuntimeError("devices.yaml devices must be a non-empty mapping")

    for device_id, info in data["devices"].items():
        if "internal" not in info or not isinstance(info["internal"], dict):
            raise RuntimeError(f"{device_id}: missing internal section")
        internal = info["internal"]
        if "cmd_topic" not in internal or "state_topic" not in internal:
            raise RuntimeError(f"{device_id}: internal must include cmd_topic and state_topic")

        if "poll" in internal:
            poll = internal["poll"]
            for k in ("topic", "payload", "interval_s"):
                if k not in poll:
                    raise RuntimeError(f"{device_id}: poll missing key {k}")

    return data


class Gateway:
    def __init__(self) -> None:
        self.registry = load_registry(REGISTRY_PATH)
        self.devices: Dict[str, Dict[str, Any]] = self.registry["devices"]

        self.std_set_to_device: Dict[str, str] = {}
        self.vendor_state_to_device: Dict[str, str] = {}
        self.last_state: Dict[str, str] = {}

        for device_id, info in self.devices.items():
            self.std_set_to_device[std_set_topic(device_id)] = device_id
            state_topic = info["internal"]["state_topic"]
            self.vendor_state_to_device[state_topic] = device_id

        self._lock = threading.Lock()
        self.mqtt_connected = False

        self.client = mqtt.Client(client_id=f"capstone-gateway-{int(time.time())}")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self._poll_thread: Optional[threading.Thread] = None

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"[MQTT] Connect failed rc={rc}")
            return

        self.mqtt_connected = True
        print(f"[MQTT] Connected to {BROKER_HOST}:{BROKER_PORT}")

        for device_id, info in self.devices.items():
            set_t = std_set_topic(device_id)
            vendor_state_t = info["internal"]["state_topic"]
            client.subscribe(set_t, qos=0)
            client.subscribe(vendor_state_t, qos=0)
            print(f"[SUB] {set_t}")
            print(f"[SUB] {vendor_state_t}")

    def on_disconnect(self, client, userdata, rc):
        self.mqtt_connected = False
        print(f"[MQTT] Disconnected rc={rc}")

    def publish_standard_status(self, device_id: str, state: str):
        topic = std_status_topic(device_id)
        payload = json.dumps({"state": state, "ts": now_ts()})
        self.client.publish(topic, payload, qos=0, retain=True)
        print(f"[PUB] {topic} <- {payload} (retained)")

    def publish_vendor_command(self, device_id: str, cmd: str):
        info = self.devices[device_id]
        internal = info["internal"]
        cmd_topic = internal["cmd_topic"]

        self.client.publish(cmd_topic, cmd, qos=0, retain=False)
        print(f"[CMD] {device_id}: {cmd_topic} <- {cmd}")

        if "poll" in internal:
            poll = internal["poll"]
            self.client.publish(poll["topic"], poll["payload"], qos=0, retain=False)

    def handle_standard_set(self, topic: str, payload: bytes):
        device_id = self.std_set_to_device[topic]
        cmd = parse_standard_command(payload)

        if cmd is None:
            print(f"[WARN] Bad command on {topic}: {payload!r}")
            return

        with self._lock:
            if cmd in ("on", "off") and device_id in self.last_state:
                desired = "ON" if cmd == "on" else "OFF"
                if self.last_state[device_id] == desired:
                    print(f"[INFO] {device_id} already {desired}, ignoring duplicate command")
                    return

        self.publish_vendor_command(device_id, cmd)

    def handle_vendor_state(self, topic: str, payload: bytes):
        device_id = self.vendor_state_to_device[topic]
        state = parse_vendor_state(payload)

        if state is None:
            print(f"[WARN] Could not parse vendor state for {device_id}: {payload!r}")
            return

        with self._lock:
            if self.last_state.get(device_id) == state:
                return
            self.last_state[device_id] = state

        self.publish_standard_status(device_id, state)

    def on_message(self, client, userdata, msg):
        topic = msg.topic

        if topic in self.std_set_to_device:
            self.handle_standard_set(topic, msg.payload)
            return

        if topic in self.vendor_state_to_device:
            self.handle_vendor_state(topic, msg.payload)
            return

        print(f"[INFO] Ignored message on {topic}")

    def poller_loop(self):
        next_poll: Dict[str, float] = {}
        for device_id, info in self.devices.items():
            internal = info["internal"]
            if "poll" in internal:
                interval = float(internal["poll"]["interval_s"])
                next_poll[device_id] = time.time()

        while True:
            now = time.time()
            soonest_next = None

            for device_id, info in self.devices.items():
                internal = info["internal"]
                if "poll" not in internal:
                    continue

                interval = float(internal["poll"]["interval_s"])
                if now >= next_poll[device_id]:
                    poll = internal["poll"]
                    self.client.publish(poll["topic"], poll["payload"], qos=0, retain=False)
                    next_poll[device_id] = now + interval

                if soonest_next is None or next_poll[device_id] < soonest_next:
                    soonest_next = next_poll[device_id]

            if soonest_next is None:
                time.sleep(1.0)
            else:
                sleep_for = max(0.1, soonest_next - time.time())
                time.sleep(sleep_for)

    def start(self):
        # Non-blocking MQTT loop so we can run HTTP server in same process
        self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        self.client.loop_start()

        self._poll_thread = threading.Thread(target=self.poller_loop, daemon=True)
        self._poll_thread.start()

    def stop(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass

    # Helpers for HTTP layer
    def snapshot_devices(self) -> Dict[str, Any]:
        with self._lock:
            states_copy = dict(self.last_state)
        out = {}
        for device_id, info in self.devices.items():
            out[device_id] = {
                "type": info.get("type"),
                "vendor": info.get("vendor"),
                "internal": info.get("internal"),
                "status_topic": std_status_topic(device_id),
                "set_topic": std_set_topic(device_id),
                "last_state": states_copy.get(device_id),  # "ON"/"OFF" or None
            }
        return out


# ---------------- HTTP API ----------------

class SetRequest(BaseModel):
    state: str
    user_id: Optional[str] = None
    source: Optional[str] = None


gateway = Gateway()
app = FastAPI()


@app.on_event("startup")
def _startup():
    gateway.start()


@app.on_event("shutdown")
def _shutdown():
    gateway.stop()


@app.get("/health")
def health():
    return {"ok": True, "mqtt_connected": gateway.mqtt_connected}


@app.get("/devices")
def get_devices():
    return gateway.snapshot_devices()


@app.get("/devices/{device_id}")
def get_device(device_id: str):
    devices = gateway.snapshot_devices()
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Unknown device_id")
    return devices[device_id]


@app.post("/devices/{device_id}/set")
def set_device(device_id: str, req: SetRequest):
    if device_id not in gateway.devices:
        raise HTTPException(status_code=404, detail="Unknown device_id")
    if not gateway.mqtt_connected:
        raise HTTPException(status_code=503, detail="MQTT not connected")

    # Build a standard MQTT payload (keeps it consistent with future app/habit usage)
    payload = {
        "state": req.state,
        "user_id": req.user_id,
        "source": req.source or "http",
        "ts": now_ts(),
    }

    # Publish to the SAME standard topic you already use from CLI:
    topic = std_set_topic(device_id)
    gateway.client.publish(topic, json.dumps(payload), qos=0, retain=False)

    return {"accepted": True, "device_id": device_id, "topic": topic, "payload": payload}


if __name__ == "__main__":
    # Host 0.0.0.0 so other devices on your LAN can send GET/POST requests.
    uvicorn.run(app, host="127.0.0.1", port=8000)
