#!/usr/bin/env python3

import os
from datetime import datetime

# Print HTTP headers first
print("Cache-Control: no-cache")
print("Content-Type: text/html\n")

# Get current date/time
current_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")

# Get IP address from environment variable
ip_address = os.environ.get('REMOTE_ADDR', 'Unknown')

# Print HTML content
print("<!DOCTYPE html>")
print("<html>")
print("<head>")
print("<title>Hello CGI World</title>")
print("</head>")
print("<body>")

print("<h1 align=center>Hello HTML World</h1><hr/>")
print("<p>Hello from Victoria Timofeev, Christine Le, and Ryan Soe!</p>")
print("<p>This page was generated with the Python programming language</p>")
print(f"<p>This program was generated at: {current_time}</p>")
print(f"<p>Your current IP Address is: {ip_address}</p>")

print("</body>")
print("</html>")
