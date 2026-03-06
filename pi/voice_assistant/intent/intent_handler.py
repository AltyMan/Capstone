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


class IntentAction(Enum): # enum for supported actions
    SET = "set"  # set on/off
    TOGGLE = "toggle"  # toggle state (modifies to opposite state)
    GET = "get"  # get state
    UNKNOWN = "unknown" # unrecognized


@dataclass
class Intent: # intent structure (to be returned in structure listed at top of file)
    action: IntentAction
    device: Optional[str] = None  # Name/ID
    command: Optional[str] = None  # on, off, toggle
    raw_speech: Optional[str] = None  # original text
    confidence: float = 1.0  # confidence score (0-1) -> measure accuracy

    def __repr__(self):
        return f"Intent(action={self.action.value}, device={self.device}, command={self.command}, confidence={self.confidence:.2f})"


class IntentParser: # intent parser class
    def __init__(self, config_path: Optional[str] = None, device_aliases: Optional[Dict[str, List[str]]] = None):
        self.device_aliases = {}
        self.action_patterns = []
        
        if config_path is None: # load config path
            config_path = Path(__file__).parent / "config.json"
        else:
            config_path = Path(config_path)
        
        self._load_config(config_path) # load from config
        
        if device_aliases:
            self.device_aliases.update(device_aliases) # merge custom aliases

    def _load_config(self, config_path: Path) -> None: # config loader
        # takes from JSON file "config.json" in same directory
        try:
            if not config_path.exists():
                print(f"Warning: Config file not found at {config_path}. Using minimal defaults.")
                self._set_defaults() # set as defaults if no config file is there
                return
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            devices_config = config.get("devices", {}) # load devices (aliases)
            for device_key, device_info in devices_config.items():
                primary = device_info.get("primary", device_key) # get device ID/key
                aliases = device_info.get("aliases", []) # get aliases recognized
                
                # add primary and aliases to mapping
                self.device_aliases[device_key.lower()] = primary
                for alias in aliases:
                    self.device_aliases[alias.lower()] = primary
            
            # load action patterns
            actions_config = config.get("actions", [])
            for action_config in actions_config: # for each, has a pattern, action type, and command executed
                pattern = action_config.get("pattern")
                action = action_config.get("action")
                command = action_config.get("command")
                
                if pattern and action: # if both exist
                    try:
                        intent_action = IntentAction(action) # convert action string to enum
                        self.action_patterns.append((pattern, intent_action, command)) # append to list
                    except ValueError:
                        print(f"Warning: Unknown action '{action}' in config. Skipping pattern.")
                        continue
            
            if not self.action_patterns:
                print("Warning: No valid action patterns loaded from config. Using defaults.")
                self._set_defaults()
                
        except json.JSONDecodeError as e:
            print(f"Error parsing config JSON: {e}. Using defaults.")
            self._set_defaults()
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            self._set_defaults()

    def _set_defaults(self) -> None: # minimal listed defaults in case of no config file
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

    def parse(self, speech: str) -> Intent: # parser, takes speech and returns expected intent structure
        if not speech or not isinstance(speech, str):
            return Intent(action=IntentAction.UNKNOWN, raw_speech=speech)

        speech = speech.strip()
        
        for pattern, action, default_command in self.action_patterns:
            match = re.search(pattern, speech, re.IGNORECASE) # match against pattern
            if match: # if matched, extract device name and resolve to ID
                device_name = match.group(1).strip() if match.groups() else None
                device_id = self._resolve_device(device_name)
                
                return Intent(
                    action=action,
                    device=device_id,
                    command=default_command,
                    raw_speech=speech,
                    confidence=0.9 if device_id else 0.6  # manual confidence score for now
                )
        # in the case of no pattern
        return Intent(
            action=IntentAction.UNKNOWN,
            raw_speech=speech,
            confidence=0.0
        )

    def _resolve_device(self, device_name: Optional[str]) -> Optional[str]: # device resolver, returns ID
        if not device_name:
            return None

        device_name_lower = device_name.lower().strip()

        # check exact match
        if device_name_lower in self.device_aliases:
            return self.device_aliases[device_name_lower]

        # check partial match
        for alias, device_id in self.device_aliases.items():
            if device_name_lower in alias or alias in device_name_lower:
                return device_id
        return None

    def add_device_alias(self, spoken_name: str, device_id: str, alternatives: Optional[List[str]] = None): # add alias
        self.device_aliases[spoken_name.lower()] = device_id


# global parser instance
_parser: Optional[IntentParser] = None


def get_parser() -> IntentParser: # get/create global parser instance
    global _parser
    if _parser is None:
        _parser = IntentParser()
    return _parser


def parse_intent(speech: str) -> Intent: # parse intent, return intent object from speech input
    return get_parser().parse(speech)


def run_intent_server(host: str = "127.0.0.1", port: int = 9090) -> None:
    parser = get_parser()
    print(f"Intent server listening on {host}:{port}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Intent client connected: {addr}")
                buf = b""
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break

                    buf += data
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        if not line.strip():
                            continue

                        try:
                            payload = json.loads(line.decode("utf-8"))
                            speech = str(payload.get("text", "")).strip()
                            if not speech:
                                continue

                            intent = parser.parse(speech)
                            print(f"Speech: \"{speech}\"")
                            print(f"{intent}")
                        except json.JSONDecodeError:
                            print("Warning: Received invalid JSON payload")


if __name__ == "__main__":
    run_intent_server()