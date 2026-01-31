#!/usr/bin/env python3

import os
import cgi
import cgitb
import http.cookies
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime

# Enable CGI error reporting
cgitb.enable()

# Session storage directory
SESSION_DIR = "/tmp/python_sessions"
Path(SESSION_DIR).mkdir(exist_ok=True)

# Session timeout (30 minutes)
SESSION_TIMEOUT = 1800

def get_session_id():
    """Get session ID from cookie or create a new one"""
    cookie = http.cookies.SimpleCookie()
    if 'HTTP_COOKIE' in os.environ:
        cookie.load(os.environ['HTTP_COOKIE'])
        if 'PYSESSID' in cookie:
            return cookie['PYSESSID'].value
    
    # Create new session ID
    session_id = hashlib.md5(f"{time.time()}{os.getpid()}".encode()).hexdigest()
    return session_id

def load_session(session_id):
    """Load session data from file"""
    session_file = os.path.join(SESSION_DIR, f"sess_{session_id}")
    if os.path.exists(session_file):
        # Check if session has expired
        file_age = time.time() - os.path.getmtime(session_file)
        if file_age < SESSION_TIMEOUT:
            with open(session_file, 'r') as f:
                return json.load(f)
        else:
            # Session expired, delete it
            os.remove(session_file)
    return {}

def print_header(session_id):
    """Print HTTP headers with cookie"""
    print("Cache-Control: no-cache")
    print(f"Set-Cookie: PYSESSID={session_id}; Path=/; Max-Age={SESSION_TIMEOUT}")
    print("Content-Type: text/html\n")

def main():
    # Get or create session
    session_id = get_session_id()
    
    # Load session data
    session_data = load_session(session_id)
    
    # Print header with session cookie
    print_header(session_id)
    
    # Get current data
    username = session_data.get('username', '')
    email = session_data.get('email', '')
    favorite_color = session_data.get('favorite_color', '')
    
    # Print page
    print("<!DOCTYPE html>")
    print("<html>")
    print("<head>")
    print("<title>Python Sessions - Page 2</title>")
    print("<style>")
    print("body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }")
    print("h1 { color: #333; }")
    print(".info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }")
    print("button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; margin: 10px 5px 0 0; }")
    print("button:hover { background: #0056b3; }")
    print(".link { display: inline-block; margin: 10px 10px 0 0; color: #007bff; text-decoration: none; }")
    print(".link:hover { text-decoration: underline; }")
    print(".destroy-btn { background: #dc3545; }")
    print(".destroy-btn:hover { background: #c82333; }")
    print("</style>")
    print("</head>")
    print("<body>")
    
    print("<h1>Python Sessions - Page 2</h1>")
    print("<p>This page displays the same session data stored on Page 1, demonstrating state persistence across different pages.</p>")
    
    print("<div class='info'>")
    if username or email or favorite_color:
        print("<h3>Session Data Retrieved:</h3>")
        if username:
            print(f"<p><strong>Username:</strong> {username}</p>")
        if email:
            print(f"<p><strong>Email:</strong> {email}</p>")
        if favorite_color:
            print(f"<p><strong>Favorite Color:</strong> {favorite_color}</p>")
    else:
        print("<p><strong>No session data found.</strong> Go to Page 1 to set some data.</p>")
    print("</div>")
    
    print("<div>")
    print("<a class='link' href='/hw2/python/state-python-page1.py'>Go to Page 1</a>")
    print("<form action='/hw2/python/state-python-destroy.py' method='POST' style='display: inline; background: none; padding: 0;'>")
    print("<button type='submit' class='destroy-btn'>Clear Session Data</button>")
    print("</form>")
    print("</div>")
    
    print("<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;'>")
    print(f"<p><small>Current Time: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}</small></p>")
    print(f"<p><small>Your IP Address: {os.environ.get('REMOTE_ADDR', 'Unknown')}</small></p>")
    print("</div>")
    
    print("</body>")
    print("</html>")

if __name__ == '__main__':
    main()
