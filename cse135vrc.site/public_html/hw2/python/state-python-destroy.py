#!/usr/bin/env python3

import os
import cgi
import cgitb
import http.cookies
from pathlib import Path

# Enable CGI error reporting
cgitb.enable()

# Session storage directory
SESSION_DIR = "/tmp/python_sessions"

def get_session_id():
    """Get session ID from cookie"""
    cookie = http.cookies.SimpleCookie()
    if 'HTTP_COOKIE' in os.environ:
        cookie.load(os.environ['HTTP_COOKIE'])
        if 'PYSESSID' in cookie:
            return cookie['PYSESSID'].value
    return None

def destroy_session(session_id):
    """Delete session file"""
    if session_id:
        session_file = os.path.join(SESSION_DIR, f"sess_{session_id}")
        if os.path.exists(session_file):
            os.remove(session_file)

def print_header():
    """Print HTTP headers that expire the cookie"""
    print("Cache-Control: no-cache")
    print("Set-Cookie: PYSESSID=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/")
    print("Content-Type: text/html\n")

def main():
    # Get session ID and destroy it
    session_id = get_session_id()
    destroy_session(session_id)
    
    # Print header that expires the cookie
    print_header()
    
    # Print confirmation page
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
    print("<a class='link' href='/hw2/python/state-python-page1.py'>Go to Page 1</a>")
    print("<a class='link' href='/hw2/python/state-python-page2.py'>Go to Page 2</a>")
    print("<a class='link' href='/hw2/echo-form.html'>Back to Echo Form</a>")
    print("</div>")
    
    print("</body>")
    print("</html>")

if __name__ == '__main__':
    main()
