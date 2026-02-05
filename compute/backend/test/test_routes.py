import pytest
import routes.habits
from objects.user import User
from app import create_app

"""
Testing script for verifying API habit outputs.
DOES NOT WORK
DELETE UNTESTED
"""

def test_habit_routes():
    app = create_app()

    with app.test_client() as test_client:
        
        # Habit Table Routes
                 
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
        
        # Habit Logging Routes
        
        res = test_client.post(
            '/1/logs/add?name=Sleep&reported=false'
        )
        assert res.status_code == 200
                
        res = test_client.get(
            '/1/logs'
        )
        assert res.status_code == 200
        
        res = test_client.post(
           '/1/logs/update?name=Sleep&field=self_reported&value=true' 
        )
        assert res.status_code == 200
        
        # Rules Logging Routes

        res = test_client.post(
            "/1/rules/delete?habit=Sleep"
        )
        assert res.status_code == 200
        
        res = test_client.post(
            "/1/rules/add?habit=Sleep&day=1&hour=8&minute=30&active=true"
        )

        assert res.status_code == 200
        data = res.get_json()

        print(data["result"])
        assert "Successfully added rule" in data["result"]


        res = test_client.get("/1/rules")

        assert res.status_code == 200
        data = res.get_json()

        print(data["result"])
        assert isinstance(data["result"], list)


        res = test_client.post(
            "/1/rules/update?habit=Sleep"
        )

        assert res.status_code == 200
        data = res.get_json()

        print(data["result"])
        assert "Successfully started updating" in data["result"]


        res = test_client.post(
            "/1/rules/delete?habit=Sleep"
        )

        assert res.status_code == 200
        data = res.get_json()

        print(data["result"])
        assert "Successfully deleted" in data["result"]
            