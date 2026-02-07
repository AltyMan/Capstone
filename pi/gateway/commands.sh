# Commands for GET/POST requests:

# GET REQUESTS

# Broker online/offline:
curl -s "https://raspberrypi.tailbe7155.ts.net/health"

# List devices:
curl -s "https://raspberrypi.tailbe7155.ts.net/devices"

#Get device status by ID:
curl -s "https://raspberrypi.tailbe7155.ts.net/devices/{device_id}"

# POST REQUESTS

# Change device state by ID (user and source optional):
curl -s -X POST "https://raspberrypi.tailbe7155.ts.net/devices/{device_id}/set" \
  -H "Content-Type: application/json" \
  -d '{"state":"{state}","user_id":"{user_id}","source":"{source}"}'
