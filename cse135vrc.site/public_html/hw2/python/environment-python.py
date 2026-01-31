#!/usr/bin/env python3

import os
from datetime import datetime

# Print HTTP headers first 
print("Cache-Control: no-cache")
print("Content-Type: text/plain; charset=utf-8\n")

# Print header information
print("Environment variables (Python)")
print(f"Generated at: {datetime.now().isoformat()}\n")

# Loop through and print all environment variables
for key in sorted(os.environ.keys()):
    value = os.environ[key]
    print(f"{key}={value}")
