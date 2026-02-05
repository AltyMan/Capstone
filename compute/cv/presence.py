from pypresence import Presence
import time

CLIENT_ID = "1465807911581126670"

rpc = Presence(CLIENT_ID)
rpc.connect()

rpc.update(
    state="Cooking",
    details="Writing a compiler",
    start=time.time(),
    large_image="cpu",        # asset key
    large_text="Computer Architecture",
    small_image="coffee",
    small_text="Still alive",
    buttons=[
        {"label": "GitHub", "url": "https://github.com/yourname"},
    ]
)

print("Rich Presence active")
while True:
    time.sleep(15)
