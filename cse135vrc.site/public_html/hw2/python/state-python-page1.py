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

def save_session(session_id, data):
    """Save session data to file"""
    session_file = os.path.join(SESSION_DIR, f"sess_{session_id}")
    with open(session_file, 'w') as f:
        json.dump(data, f)

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
    
    # Get form data
    form = cgi.FieldStorage()
    action = form.getvalue('action', 'display')
    
    # Handle save action
    if action == 'save':
        username = form.getvalue('username', '')
        email = form.getvalue('email', '')
        favorite_color = form.getvalue('favorite_color', '')
        
        if username:
            session_data['username'] = username
        if email:
            session_data['email'] = email
        if favorite_color:
            session_data['favorite_color'] = favorite_color
        
        save_session(session_id, session_data)
    
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
    print("<title>Python Sessions - Page 1</title>")
    print("</head>")
    print("<body>")
    
    print("<h1>Python Sessions - Page 1</h1>")
    print("<p>This page demonstrates server-side session management using Python CGI with cookies.</p>")
    
    print("<div>")
    if username or email or favorite_color:
        print("<h3>Current Session Data:</h3>")
        if username:
            print(f"<p><b>Username:</b> {username}</p>")
        if email:
            print(f"<p><b>Email:</b> {email}</p>")
        if favorite_color:
            print(f"<p><b>Favorite Color:</b> {favorite_color}</p>")
    else:
        print("<p><b>No session data set yet.</b> Please enter some information below.</p>")
    print("</div>")
    
    print("<form action='/hw2/python/state-python-page1.py' method='POST'>")
    print("<input type='hidden' name='action' value='save'>")
    print("<h3>Enter Your Information:</h3>")
    print("<label for='username'>Username:</label>")
    print(f"<input type='text' id='username' name='username' value='{username}' placeholder='Enter your username'>")
    print("<label for='email'>Email:</label>")
    print(f"<input type='email' id='email' name='email' value='{email}' placeholder='Enter your email'>")
    print("<label for='favorite_color'>Favorite Color:</label>")
    print(f"<input type='text' id='favorite_color' name='favorite_color' value='{favorite_color}' placeholder='Enter your favorite color'>")
    print("<button type='submit'>Save Data</button>")
    print("</form>")
    
    print("<br/><br/>")
    print("<a href='/hw2/python/state-python-page2.py'>Go to Page 2</a><br/>")
    print("<form action='/hw2/python/state-python-destroy.py' method='POST'>")
    print("<button type='submit'>Clear Session Data</button>")
    print("</form>")
    
    print("<hr/>")
    print(f"<p>Current Time: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}</p>")
    print(f"<p>Your IP Address: {os.environ.get('REMOTE_ADDR', 'Unknown')}</p>")
    
    print("</body>")
    print("</html>")

if __name__ == '__main__':
    main()
