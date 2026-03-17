# Convert voice-recognized speech to intents/commands:
#    Ex. "Turn on the bedroom lights" 
#    Output: Intent(action="set", device="bedroom_lights", command="on")

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import re
from enum import Enum
from pathlib import Path
import json
import socket
import time
import paho.mqtt.client as mqtt

MQTT_BROKER_HOST = "127.0.0.1"
MQTT_BROKER_PORT = 1883
TARGET_PLUGS = ("plug1", "plug2")

class IntentAction(Enum): 
    SET = "set"  
    TOGGLE = "toggle"  
    GET = "get"  
    UNKNOWN = "unknown" 

@dataclass
class Intent: 
    action: IntentAction
    device: Optional[str] = None  
    command: Optional[str] = None  
    raw_speech: Optional[str] = None  
    confidence: float = 1.0  

    def __repr__(self):
        return f"Intent(action={self.action.value}, device={self.device}, command={self.command}, confidence={self.confidence:.2f})"

class IntentParser: 
    def __init__(self, config_path: Optional[str] = None, device_aliases: Optional[Dict[str, List[str]]] = None):
        self.device_aliases = {}
        self.action_patterns = []
        
        if config_path is None: 
            config_path = Path(__file__).parent / "config.json"
        else:
            config_path = Path(config_path)
        
        self._load_config(config_path) 
        
        if device_aliases:
            self.device_aliases.update(device_aliases) 

    def _load_config(self, config_path: Path) -> None: 
        try:
            if not config_path.exists():
                self._set_defaults() 
                return
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            devices_config = config.get("devices", {}) 
            for device_key, device_info in devices_config.items():
                primary = device_info.get("primary", device_key) 
                aliases = device_info.get("aliases", []) 
                
                self.device_aliases[device_key.lower()] = primary
                for alias in aliases:
                    self.device_aliases[alias.lower()] = primary
            
            actions_config = config.get("actions", [])
            for action_config in actions_config: 
                pattern = action_config.get("pattern")
                action = action_config.get("action")
                command = action_config.get("command")
                
                if pattern and action: 
                    try:
                        intent_action = IntentAction(action) 
                        self.action_patterns.append((pattern, intent_action, command)) 
                    except ValueError:
                        continue
            
            if not self.action_patterns:
                self._set_defaults()
                
        except Exception:
            self._set_defaults()

    def _set_defaults(self) -> None: 
        default_aliases = {
            "bedroom light": "bedroom_light", "bedroom": "bedroom_light",
            "bedroom lights": "bedroom_light", "bedroom lamp": "bedroom_light",
            "plug one": "plug1", "plug 1": "plug1", "first plug": "plug1",
            "plug two": "plug2", "plug 2": "plug2", "second plug": "plug2",
        }
        self.device_aliases = default_aliases
        
        self.action_patterns = [
            (r"turn\s+(?:on|up)\s+(?:the\s+)?(.+)", IntentAction.SET, "on"),
            (r"turn\s+off\s+(?:the\s+)?(.+)", IntentAction.SET, "off"),
            (r"toggle\s+(?:the\s+)?(.+)", IntentAction.TOGGLE, "toggle"),
            (r"(?:what'?s|get|check)\s+(?:the\s+)?(?:status|state)\s+of\s+(?:the\s+)?(.+)", IntentAction.GET, None),
            (r"is\s+(?:the\s+)?(.+)\s+(?:on|off)\??", IntentAction.GET, None),
        ]

    def parse(self, speech: str) -> Intent: 
        if not speech or not isinstance(speech, str):
            return Intent(action=IntentAction.UNKNOWN, raw_speech=speech)

        speech = speech.strip()
        
        for pattern, action, default_command in self.action_patterns:
            match = re.search(pattern, speech, re.IGNORECASE) 
            if match: 
                device_name = match.group(1).strip() if match.groups() else None
                device_id = self._resolve_device(device_name)
                return Intent(
                    action=action, device=device_id, command=default_command,
                    raw_speech=speech, confidence=0.9 if device_id else 0.6  
                )
        return Intent(action=IntentAction.UNKNOWN, raw_speech=speech, confidence=0.0)

    def _resolve_device(self, device_name: Optional[str]) -> Optional[str]: 
        if not device_name: return None
        device_name_lower = device_name.lower().strip()
        if device_name_lower in self.device_aliases:
            return self.device_aliases[device_name_lower]
        for alias, device_id in self.device_aliases.items():
            if device_name_lower in alias or alias in device_name_lower:
                return device_id
        return None

_parser: Optional[IntentParser] = None

def get_parser() -> IntentParser: 
    global _parser
    if _parser is None: _parser = IntentParser()
    return _parser

def std_set_topic(device_id: str) -> str:
    return f"/home/{device_id}/set"

def _infer_target_plug_from_speech(speech: Optional[str]) -> Optional[str]:
    if not speech: return None
    text = speech.lower()
    if re.search(r"\b(plug\s*1|plug\s*one|first\s*plug|plug1)\b", text): return "plug1"
    if re.search(r"\b(plug\s*2|plug\s*two|second\s*plug|plug2)\b", text): return "plug2"
    if re.search(r"\b(plug\s*3|plug\s*three|third\s*plug|plug3)\b", text): return "plug3"
    return None

def publish_intent_to_mqtt(client: mqtt.Client, intent: Intent) -> None:
    if intent.action == IntentAction.SET and intent.command in ("on", "off"):
        command = intent.command
    elif intent.action == IntentAction.TOGGLE:
        command = "toggle"
    else:
        return

    target_device = intent.device if intent.device in TARGET_PLUGS else _infer_target_plug_from_speech(intent.raw_speech)

    if target_device is None:
        print("[MQTT] Skipped publish: no target plug resolved")
        return

    topic = std_set_topic(target_device)
    client.publish(topic, command, qos=0, retain=False)
    print(f"[MQTT] {topic} <- {command}")

def generate_response_text(intent: Intent, target_device: Optional[str]) -> str:
    # This 0.4s file wakes up the physical amplifier on the ESP32!
    base = "silence.mp3,"
    
    # Error states map to a single file
    if intent.action == IntentAction.UNKNOWN:
        return base + "i-m-sorry-i-didn-t-understand-that-command.mp3"
    
    if not target_device:
        return base + "sorry-this-device-is-not-recognized.mp3"
    
    # Determine the target plug file
    device_file = None
    if target_device == "plug1":
        device_file = "plug-one.mp3"
    elif target_device == "plug2":
        device_file = "plug-two.mp3"
    else:
        device_file = "plug-three.mp3"
    #device_file = "plug-one.mp3" if target_device == "plug1" else "plug-two.mp3"
    
    # Combine the action file with the target plug file
    if intent.action == IntentAction.SET:
        if intent.command == "on":
            return base + f"turning-on.mp3,{device_file}"
        else:
            return base + f"turning-off.mp3,{device_file}"
    elif intent.action == IntentAction.TOGGLE:
        return base + f"toggling.mp3,{device_file}"
    elif intent.action == IntentAction.GET:
        return base + f"checking.mp3,{device_file}"
    
    return base + "i-m-sorry-i-didn-t-understand-that-command.mp3"

def run_intent_server(host: str = "127.0.0.1", port: int = 9090) -> None:
    parser = get_parser()
    print(f"Intent server listening on {host}:{port}...")

    mqtt_client = mqtt.Client(client_id=f"intent-handler-{int(time.time())}")
    try:
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        mqtt_client.loop_start()
        print(f"MQTT connected to {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    except ConnectionRefusedError:
        print(f"[WARNING] MQTT Broker offline at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}. Running without MQTT.")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen()

            while True:
                conn, addr = server.accept()
                with conn:
                    buf = b""
                    while True:
                        data = conn.recv(4096)
                        if not data: break
                        buf += data
                        
                        while b"\n" in buf:
                            line, buf = buf.split(b"\n", 1)
                            if not line.strip(): continue

                            try:
                                payload = json.loads(line.decode("utf-8"))
                                speech = str(payload.get("text", "")).strip()
                                if not speech:
                                    conn.sendall(b"No speech detected.\n")
                                    continue

                                intent = parser.parse(speech)
                                target_device = intent.device if intent.device in TARGET_PLUGS else _infer_target_plug_from_speech(intent.raw_speech)
                                
                                publish_intent_to_mqtt(mqtt_client, intent)
                                
                                # Send the friendly string back to command_listener.py!
                                reply = generate_response_text(intent, target_device)
                                conn.sendall((reply + "\n").encode("utf-8"))
                                
                            except json.JSONDecodeError:
                                conn.sendall(b"I encountered an error parsing the intent.\n")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    run_intent_server()