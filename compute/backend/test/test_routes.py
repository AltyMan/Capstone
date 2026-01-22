import pytest
import routes.habits
from objects.user import User
from app import create_app

"""
Testing script for verifying API habit outputs.
DOES NOT WORK
"""

@pytest.fixture
def client():
    return create_app().test_client()

def test_habit_routes(client):
    test_client = client
            
    res = test_client.post(
        "/1/habits/add?name=Sleep"
    )

    assert res.status_code == 200
    assert "successfully added Habit Sleep" in res.json["response"]

    res = client.get("/1/habits")
    assert res.status_code == 200

    habits = res.json["habits"]
    assert len(habits) == 1
    assert habits[0]["name"] == "Sleep"
    