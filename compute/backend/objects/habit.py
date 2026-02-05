from dataclasses import dataclass

@dataclass
class Habit:
    """
    Represents a trackable habit or device-associated activity.

    A Habit can either correspond to a physical device (e.g., IoT sensor,
    smart button, etc.) or a logical/manual habit. It stores identifying
    metadata along with simple progress tracking such as the current streak.

    Attributes
    ----------
    habit_name : str
        Human-readable name of the habit.
    assoc_dev_id : Any
        Identifier of the associated device, if this habit is tied to hardware.
        None if not device-backed.
    assoc_mqtt_topic : str
        MQTT topic used to publish/subscribe to events for this habit.
        Empty if not applicable.
    habit_id : str
        Unique identifier for this habit instance.
    is_device : bool
        True if this habit is linked to a physical device, False if it is manual.
    streak : int
        Current consecutive completion count for the habit.
    """
    habit_name: str = ""
    assoc_dev_id = None
    assoc_mqtt_topic: str = ""
    habit_id: str = None
    is_device: bool = True
    streak: int = 0
    