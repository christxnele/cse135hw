package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/url"
	"os"
	"strings"
	"time"
)

const sessionDir = "/tmp/go_sessions"
const sessionTimeout = 1800

func generateSessionID() string {
	bytes := make([]byte, 16)
	rand.Read(bytes)
	return hex.EncodeToString(bytes)
}

func getSessionIDFromCookie() string {
	cookie := os.Getenv("HTTP_COOKIE")
	if cookie == "" {
		return ""
	}
	for _, part := range strings.Split(cookie, ";") {
		part = strings.TrimSpace(part)
		if strings.HasPrefix(part, "GOSESSID=") {
			return strings.TrimPrefix(part, "GOSESSID=")
		}
	}
	return ""
}

func getSessionFilePath(sessionID string) string {
	return sessionDir + "/sess_" + sessionID
}

func loadSession(sessionID string) map[string]string {
	data := make(map[string]string)
	if sessionID == "" {
		return data
	}
	filePath := getSessionFilePath(sessionID)
	info, err := os.Stat(filePath)
	if err != nil {
		return data
	}
	if time.Since(info.ModTime()).Seconds() > sessionTimeout {
		os.Remove(filePath)
		return data
	}
	content, err := os.ReadFile(filePath)
	if err != nil {
		return data
	}
	json.Unmarshal(content, &data)
	return data
}

func saveSession(sessionID string, data map[string]string) error {
	os.MkdirAll(sessionDir, 0755)
	content, _ := json.Marshal(data)
	return os.WriteFile(getSessionFilePath(sessionID), content, 0644)
}

func destroySession(sessionID string) {
	if sessionID != "" {
		os.Remove(getSessionFilePath(sessionID))
	}
}

func printHeader(sessionID string, destroy bool) {
	fmt.Println("Cache-Control: no-cache")
	if destroy {
		fmt.Println("Set-Cookie: GOSESSID=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/")
	} else {
		fmt.Printf("Set-Cookie: GOSESSID=%s; Path=/; Max-Age=%d\n", sessionID, sessionTimeout)
	}
	fmt.Println("Content-Type: text/html")
	fmt.Println("")
}

func escapeHTML(s string) string {
	s = strings.ReplaceAll(s, "&", "&amp;")
	s = strings.ReplaceAll(s, "<", "&lt;")
	s = strings.ReplaceAll(s, ">", "&gt;")
	s = strings.ReplaceAll(s, "\"", "&quot;")
	return s
}

func printPage1(sessionData map[string]string) {
	username := escapeHTML(sessionData["username"])
	email := escapeHTML(sessionData["email"])
	favoriteColor := escapeHTML(sessionData["favorite_color"])

	fmt.Println(`<!DOCTYPE html>
<html>
<head><title>Go Sessions - Page 1</title></head>
<body>
<h1>Go Sessions - Page 1</h1>`)

	if username != "" || email != "" || favoriteColor != "" {
		fmt.Println("<h3>Current Session Data:</h3>")
		if username != "" {
			fmt.Printf("<p>Username: %s</p>\n", username)
		}
		if email != "" {
			fmt.Printf("<p>Email: %s</p>\n", email)
		}
		if favoriteColor != "" {
			fmt.Printf("<p>Favorite Color: %s</p>\n", favoriteColor)
		}
	} else {
		fmt.Println("<p>No session data set yet.</p>")
	}

	fmt.Printf(`<hr>
<h3>Enter Your Information:</h3>
<form action='/hw2/go/state-go.cgi' method='POST'>
<input type='hidden' name='action' value='save'>
<label>Username <input type='text' name='username' value='%s'></label><br><br>
<label>Email <input type='email' name='email' value='%s'></label><br><br>
<label>Favorite Color <input type='text' name='favorite_color' value='%s'></label><br><br>
<button type='submit'>Save Data</button>
</form>

<p><a href='/hw2/go/state-go.cgi?page=2'>Go to Page 2</a></p>

<form action='/hw2/go/state-go.cgi' method='POST'>
<input type='hidden' name='action' value='destroy'>
<button type='submit'>Clear Session Data</button>
</form>

</body>
</html>`, username, email, favoriteColor)
}

func printPage2(sessionData map[string]string) {
	username := escapeHTML(sessionData["username"])
	email := escapeHTML(sessionData["email"])
	favoriteColor := escapeHTML(sessionData["favorite_color"])

	fmt.Println(`<!DOCTYPE html>
<html>
<head><title>Go Sessions - Page 2</title></head>
<body>
<h1>Go Sessions - Page 2</h1>`)

	if username != "" || email != "" || favoriteColor != "" {
		fmt.Println("<h3>Session Data Retrieved:</h3>")
		if username != "" {
			fmt.Printf("<p>Username: %s</p>\n", username)
		}
		if email != "" {
			fmt.Printf("<p>Email: %s</p>\n", email)
		}
		if favoriteColor != "" {
			fmt.Printf("<p>Favorite Color: %s</p>\n", favoriteColor)
		}
	} else {
		fmt.Println("<p>No session data found. Go to Page 1 to set some data.</p>")
	}

	fmt.Println(`<p><a href='/hw2/go/state-go.cgi?page=1'>Go to Page 1</a></p>

<form action='/hw2/go/state-go.cgi' method='POST'>
<input type='hidden' name='action' value='destroy'>
<button type='submit'>Clear Session Data</button>
</form>

</body>
</html>`)
}

func printDestroyPage() {
	fmt.Println(`<!DOCTYPE html>
<html>
<head><title>Go Session Destroyed</title></head>
<body>
<h1>Session Destroyed</h1>
<p>Your session data has been cleared.</p>
<p><a href='/hw2/go/state-go.cgi?page=1'>Go to Page 1</a></p>
<p><a href='/hw2/go/state-go.cgi?page=2'>Go to Page 2</a></p>
</body>
</html>`)
}

func main() {
	method := os.Getenv("REQUEST_METHOD")
	queryString := os.Getenv("QUERY_STRING")
	contentType := os.Getenv("CONTENT_TYPE")

	queryParams, _ := url.ParseQuery(queryString)
	page := queryParams.Get("page")
	if page == "" {
		page = "1"
	}

	sessionID := getSessionIDFromCookie()
	if sessionID == "" {
		sessionID = generateSessionID()
	}

	formData := make(map[string]string)
	if method == "POST" {
		body, _ := io.ReadAll(os.Stdin)
		if strings.Contains(contentType, "application/json") {
			json.Unmarshal(body, &formData)
		} else {
			values, _ := url.ParseQuery(string(body))
			for key, val := range values {
				formData[key] = val[0]
			}
		}
	}

	action := formData["action"]
	if action == "" {
		action = queryParams.Get("action")
	}

	if action == "destroy" {
		destroySession(sessionID)
		printHeader(sessionID, true)
		printDestroyPage()
		return
	}

	sessionData := loadSession(sessionID)

	if action == "save" {
		if val := formData["username"]; val != "" {
			sessionData["username"] = val
		}
		if val := formData["email"]; val != "" {
			sessionData["email"] = val
		}
		if val := formData["favorite_color"]; val != "" {
			sessionData["favorite_color"] = val
		}
		saveSession(sessionID, sessionData)
	}

	printHeader(sessionID, false)

	if page == "2" {
		printPage2(sessionData)
	} else {
		printPage1(sessionData)
	}
}
