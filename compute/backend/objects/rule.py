from dataclasses import dataclass

@dataclass
class Rule:
    day: int
    hour: int
    minute: int
    active: bool