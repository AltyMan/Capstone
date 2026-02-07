# Commands for GET/POST requests:

# GET REQUESTS

# Broker online/offline:
curl -s "https://raspberrypi.tailbe7155.ts.net/health"
# Output: {"ok":true,"mqtt_connected":true}

# List devices:
curl -s "https://raspberrypi.tailbe7155.ts.net/devices"
# Output:
# {"plug1":{"type":"plug","vendor":"kasa","internal":{"cmd_topic":"/hs105/switch",
# "state_topic":"/hs105/switch"},"status_topic":"/home/plug1/status","set_topic":"/home/plug1/set","last_state":null},
# "plug2":{"type":"plug","vendor":"shelly","internal":{"cmd_topic":"shellyplugusg4/command/switch:0","state_topic":"shellyplugusg4/status/switch:0",
# "poll":{"topic":"shellyplugusg4/command","payload":"status_update","interval_s":2}},"status_topic":"/home/plug2/status","set_topic":"/home/plug2/set","last_state":"ON"}}

#Get device status by ID:
curl -s "https://raspberrypi.tailbe7155.ts.net/devices/{device_id}"
# Output:
# {"type":"plug","vendor":"shelly","internal":{"cmd_topic":"shellyplugusg4/command/switch:0","state_topic":"shellyplugusg4/status/switch:0",
# "poll":{"topic":"shellyplugusg4/command","payload":"status_update","interval_s":2}},"status_topic":"/home/plug2/status","set_topic":"/home/plug2/set","last_state":"ON"}

# POST REQUESTS

# Change device state by ID (user and source optional):
curl -s -X POST "https://raspberrypi.tailbe7155.ts.net/devices/{device_id}/set" \
  -H "Content-Type: application/json" \
  -d '{"state":"{state}","user_id":"{user_id}","source":"{source}"}'
# Output: {"accepted":true,"device_id":"plug2","topic":"/home/plug2/set","payload":{"state":"ON","user_id":"0","source":"local","ts":1770498001}}
