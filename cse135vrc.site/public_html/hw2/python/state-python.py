#!/usr/bin/env python3

# Redirect to state-python-page1.py
# This file exists for backwards compatibility

print("Status: 302 Found")
print("Location: /hw2/python/state-python-page1.py")
print("Content-Type: text/html\n")
print("<!DOCTYPE html>")
print("<html><head><title>Redirecting...</title></head>")
print("<body><p>Redirecting to <a href='/hw2/python/state-python-page1.py'>state-python-page1.py</a>...</p></body>")
print("</html>")
