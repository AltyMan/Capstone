import pandas as pd
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from dataclasses import dataclass

from objects.rule import Rule
from utils.time import fix_time

@dataclass
class Habit:
    habit_name: str = ""
    assoc_dev_id = None
    assoc_mqtt_topic: str = ""
    habit_id: str = None
    is_device: bool = True
    streak: int = 0
    