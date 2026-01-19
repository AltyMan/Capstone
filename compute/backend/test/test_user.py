from objects.user import User
import pytest
from db.init_db import init_db

@pytest.fixture(scope="session", autouse=True)
def init_database():
    init_db()

def test_create_user():
    user = User.create()

    assert user.id is not None
    assert isinstance(user.id, int)


def test_add_and_get_habit():
    user = User.create()

    user.add_habit("Meditation")
    habits = user.get_habits()

    assert len(habits) == 1
    assert habits[0].habit_name == "Meditation"


def test_update_habit():
    user = User.create()
    user.add_habit("Running")

    user.update_habit("name", "Jogging", "Running")
    habits = user.get_habits()

    assert habits[0].habit_name == "Jogging"


def test_delete_habit():
    user = User.create()
    user.add_habit("Reading")

    user.delete_habit("Reading")
    habits = user.get_habits()

    assert habits == []


def test_log_habit():
    user = User.create()
    user.add_habit("Sleep")

    user.log_habit("Sleep", state="OK")
    logs = user.get_habit_logs("Sleep")

    assert len(logs) == 1

    row = logs.iloc[0]
    assert row["state"] == "OK"
    assert bool(row["self_reported"]) is True
