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

def destroy_session(session_id):
    """Delete session file"""
    session_file = os.path.join(SESSION_DIR, f"sess_{session_id}")
    if os.path.exists(session_file):
        os.remove(session_file)

def print_header(session_id, destroy=False):
    """Print HTTP headers with cookie"""
    print("Cache-Control: no-cache")
    
    if destroy:
        # Set cookie to expire immediately
        print("Set-Cookie: PYSESSID=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/")
    else:
        # Set cookie with session ID
        print(f"Set-Cookie: PYSESSID={session_id}; Path=/; Max-Age={SESSION_TIMEOUT}")
    
    print("Content-Type: text/html\n")

def get_form_data():
    """Get form data from request"""
    form = cgi.FieldStorage()
    return form

def main():
    # Get current action
    form = get_form_data()
    action = form.getvalue('action', 'display')
    page = form.getvalue('page', '1')
    
    # Get or create session
    session_id = get_session_id()
    
    # Handle destroy action
    if action == 'destroy':
        destroy_session(session_id)
        print_header(session_id, destroy=True)
        print_destroy_page()
        return
    
    # Load session data
    session_data = load_session(session_id)
    
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
    
    # Display appropriate page
    if page == '1':
        print_page_1(session_data)
    elif page == '2':
        print_page_2(session_data)

def print_page_1(session_data):
    """Print page 1 - form to enter data"""
    username = session_data.get('username', '')
    email = session_data.get('email', '')
    favorite_color = session_data.get('favorite_color', '')
    
    print("<!DOCTYPE html>")
    print("<html>")
    print("<head>")
    print("<title>Python Sessions - Page 1</title>")
    print("<style>")
    print("body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }")
    print("h1 { color: #333; }")
    print("form { background: #f4f4f4; padding: 20px; border-radius: 5px; margin: 20px 0; }")
    print("label { display: block; margin: 10px 0 5px; font-weight: bold; }")
    print("input[type='text'], input[type='email'] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }")
    print("button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; margin: 10px 5px 0 0; }")
    print("button:hover { background: #0056b3; }")
    print(".info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }")
    print(".link { display: inline-block; margin: 10px 10px 0 0; color: #007bff; text-decoration: none; }")
    print(".link:hover { text-decoration: underline; }")
    print(".destroy-btn { background: #dc3545; }")
    print(".destroy-btn:hover { background: #c82333; }")
    print("</style>")
    print("</head>")
    print("<body>")
    
    print("<h1>Python Sessions - Page 1</h1>")
    print("<p>This page demonstrates server-side session management using Python CGI with cookies.</p>")
    
    print("<div class='info'>")
    if username or email or favorite_color:
        print("<h3>Current Session Data:</h3>")
        if username:
            print(f"<p><strong>Username:</strong> {username}</p>")
        if email:
            print(f"<p><strong>Email:</strong> {email}</p>")
        if favorite_color:
            print(f"<p><strong>Favorite Color:</strong> {favorite_color}</p>")
    else:
        print("<p><strong>No session data set yet.</strong> Please enter some information below.</p>")
    print("</div>")
    
    print("<form action='/hw2/python/state-python.py' method='POST'>")
    print("<input type='hidden' name='action' value='save'>")
    print("<input type='hidden' name='page' value='1'>")
    print("<h3>Enter Your Information:</h3>")
    print("<label for='username'>Username:</label>")
    print(f"<input type='text' id='username' name='username' value='{username}' placeholder='Enter your username'>")
    print("<label for='email'>Email:</label>")
    print(f"<input type='email' id='email' name='email' value='{email}' placeholder='Enter your email'>")
    print("<label for='favorite_color'>Favorite Color:</label>")
    print(f"<input type='text' id='favorite_color' name='favorite_color' value='{favorite_color}' placeholder='Enter your favorite color'>")
    print("<button type='submit'>Save Data</button>")
    print("</form>")
    
    print("<div>")
    print("<a class='link' href='/hw2/python/state-python.py?page=2'>Go to Page 2</a>")
    print("<form action='/hw2/python/state-python.py' method='POST' style='display: inline; background: none; padding: 0;'>")
    print("<input type='hidden' name='action' value='destroy'>")
    print("<button type='submit' class='destroy-btn'>Clear Session Data</button>")
    print("</form>")
    print("</div>")
    
    print("<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;'>")
    print(f"<p><small>Current Time: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}</small></p>")
    print(f"<p><small>Your IP Address: {os.environ.get('REMOTE_ADDR', 'Unknown')}</small></p>")
    print("</div>")
    
    print("</body>")
    print("</html>")

def print_page_2(session_data):
    """Print page 2 - display stored data"""
    username = session_data.get('username', '')
    email = session_data.get('email', '')
    favorite_color = session_data.get('favorite_color', '')
    
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
    print("<a class='link' href='/hw2/python/state-python.py?page=1'>Go to Page 1</a>")
    print("<form action='/hw2/python/state-python.py' method='POST' style='display: inline; background: none; padding: 0;'>")
    print("<input type='hidden' name='action' value='destroy'>")
    print("<button type='submit' class='destroy-btn'>Clear Session Data</button>")
    print("</form>")
    print("</div>")
    
    print("<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;'>")
    print(f"<p><small>Current Time: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}</small></p>")
    print(f"<p><small>Your IP Address: {os.environ.get('REMOTE_ADDR', 'Unknown')}</small></p>")
    print("</div>")
    
    print("</body>")
    print("</html>")

def print_destroy_page():
    """Print session destroyed confirmation page"""
    print("<!DOCTYPE html>")
    print("<html>")
    print("<head>")
    print("<title>Python Session Destroyed</title>")
    print("<style>")
    print("body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }")
    print("h1 { color: #333; }")
    print(".success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; border: 1px solid #c3e6cb; }")
    print(".link { display: inline-block; margin: 10px 10px 0 0; color: #007bff; text-decoration: none; }")
    print(".link:hover { text-decoration: underline; }")
    print("</style>")
    print("</head>")
    print("<body>")
    
    print("<h1>Session Destroyed</h1>")
    print("<div class='success'>")
    print("<p><strong>Success!</strong> Your session data has been cleared.</p>")
    print("</div>")
    
    print("<div>")
    print("<a class='link' href='/hw2/python/state-python.py?page=1'>Go to Page 1</a>")
    print("<a class='link' href='/hw2/python/state-python.py?page=2'>Go to Page 2</a>")
    print("<a class='link' href='/hw2/echo-form.html'>Back to Echo Form</a>")
    print("</div>")
    
    print("</body>")
    print("</html>")

if __name__ == '__main__':
    main()
