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

    NOTE FOR HABO FRONTEND INTEGRATION:
    -----------------------------------
    The Flutter Habo app consumes this dataclass via the HTTP layer
    (`HttpHabitRepository` in `mobile/Habo/lib/repositories/http_habit_repository.dart`).

    Right now the mobile code only relies on:
      - ``habit_name``  → mapped to Habo's ``HabitData.title``
      - ``habit_id``    → mapped to Habo's ``HabitData.id`` (parsed as int if possible)
      - ``is_device``   → used to decide whether the habit is archived or not

    If you later want the mobile app to persist more of Habo's rich fields
    (cue, routine, reward, two-day rule, numeric targets, categories, etc.),
    you have two options:
      1. Extend this dataclass with additional attributes that mirror Habo's
         ``HabitData`` model, and return them from the API.
      2. Introduce a separate "HaboHabit" DTO that has the full schema and
         convert between repository rows and that DTO before serializing.

    See the TODO comments in `backend/routes/habits.py` for the expected
    JSON contract from the mobile app's point of view.
    """

    habit_name: str = ""
    assoc_dev_id = None
    assoc_mqtt_topic: str = ""
    habit_id: str | None = None
    is_device: bool = True
    streak: int = 0
    