from app import app

def print_response(label, response):
    print(f"\n=== {label} ===")
    print("Status:", response.status_code)
    try:
        print("JSON:", response.get_json())
    except Exception:
        print("Raw:", response.data.decode())
    
with app.test_client() as client:
    
# GET REQUESTS

    # GET /<user_id>  (update user)
    res = client.get("/1")
    print_response("GET update user", res)


    # GET /<user_id>/get-habits
    res = client.get("/1/get-habits")
    print_response("GET get-habits", res)

    # GET /<user_id>/get-habit/<habit_name>/rules
    res = client.get("/1/get-habit/Lamp/rules")
    print_response("GET habit rules (Lamp)", res)

    # GET /<user_id>/get-habit-rules
    res = client.get("/1/get-habit-rules")
    print_response("GET all habit rules", res)

    # GET /<user_id>/summary
    res = client.get("/1/summary")
    print_response("GET summary", res)

    # GET /<user_id>/trends
    res = client.get("/1/trends")
    print_response("GET trends", res)

    # GET /<user_id>/streak
    res = client.get("/1/streak")
    print_response("GET streak", res)
    
# POST REQUESTS

    # POST /<user_id>/log-habit
    res = client.post("/1/log-habit?habit=Lamp")
    print_response("POST log-habit", res)

    # POST /<user_id>/reschedule
    res = client.post("/1/reschedule")
    print_response("POST reschedule", res)
