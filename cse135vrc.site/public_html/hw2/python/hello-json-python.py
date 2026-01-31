#!/usr/bin/env python3

import os
import json
from datetime import datetime

# Print HTTP headers first 
print("Cache-Control: no-cache")
print("Content-Type: application/json\n")

# Get current date/time in ISO format
current_time = datetime.now().isoformat()

# Get IP address from environment variable
ip_address = os.environ.get('REMOTE_ADDR', 'unknown')

# Create JSON response
data = {
    "team": "Victoria, Ryan, and Christine",
    "language": "Python",
    "generated_at": current_time,
    "ip": ip_address
}

# Print JSON
print(json.dumps(data))
