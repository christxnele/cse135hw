#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime
from urllib.parse import parse_qs

# Print HTTP headers first 
print("Cache-Control: no-cache")
print("Content-Type: application/json\n")

# Get request method
method = os.environ.get('REQUEST_METHOD', 'GET')

# Get content type
content_type = os.environ.get('CONTENT_TYPE', '')

# Initialize data dictionary
data = {}

# Handle GET request
if method == 'GET':
    query_string = os.environ.get('QUERY_STRING', '')
    if query_string:
        # Parse query string
        parsed = parse_qs(query_string)
        # Convert lists to single values if only one item
        data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

# Handle POST, PUT, DELETE requests
else:
    content_length = int(os.environ.get('CONTENT_LENGTH', 0))
    if content_length > 0:
        raw_body = sys.stdin.read(content_length)
        
        # Check if content type is JSON
        if 'application/json' in content_type:
            try:
                data = json.loads(raw_body)
            except json.JSONDecodeError:
                data = {"raw": raw_body}
        else:
            # Parse as form-urlencoded
            parsed = parse_qs(raw_body)
            data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

# Build response
response = {
    "language": "Python",
    "method": method,
    "time": datetime.now().isoformat(),
    "ip": os.environ.get('REMOTE_ADDR', 'unknown'),
    "user_agent": os.environ.get('HTTP_USER_AGENT', ''),
    "data_received": data
}

# Print JSON response
print(json.dumps(response, indent=2))
