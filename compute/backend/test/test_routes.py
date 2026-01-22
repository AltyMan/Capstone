import pytest
import routes.habits
from objects.user import User
from app import create_app

"""
Testing script for verifying API habit outputs.
DOES NOT WORK
"""

def test_habit_routes():
    app = create_app()

    with app.test_client() as test_client:
                 
        res = test_client.post(
            "/1/habits/add?name=Sleep"
        )

        assert res.status_code == 200
        assert "successfully added Habit Sleep" in res.json["response"]

        res = test_client.get("/1/habits")
        assert res.status_code == 200

        habits = res.json["habits"]
        assert habits[0]["habit_name"] == "Sleep"
        
        res = test_client.post(
            '/1/habits/update?name=Sleep&field=is_device&value=true'
            )
        assert res.status_code == 200
        
    