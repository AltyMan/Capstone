from dataclasses import dataclass

@dataclass
class Rule:
    """
    Represents a scheduling rule for when a habit should occur or be checked.

    A rule specifies a day of the week and a time (hour + minute), along with
    whether the rule is currently active. These rules can be used for reminders,
    automations, or inferred behavior based on historical habit logs.

    Attributes
    ----------
    day : int
        Day of the week (typically 0-6, where 0 = Monday or Sunday depending on convention).
    hour : int
        Hour of the day in 24-hour format (0-23).
    minute : int
        Minute of the hour (0-59).
    active : bool
        Whether this rule is enabled and should be applied.
    """
    day: int
    hour: int
    minute: int
    active: bool