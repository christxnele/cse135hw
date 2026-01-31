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

func escapeHTML(s string) string {
	s = strings.ReplaceAll(s, "&", "&amp;")
	s = strings.ReplaceAll(s, "<", "&lt;")
	s = strings.ReplaceAll(s, ">", "&gt;")
	s = strings.ReplaceAll(s, "\"", "&quot;")
	return s
}

func main() {
	method := os.Getenv("REQUEST_METHOD")
	queryString := os.Getenv("QUERY_STRING")
	contentType := os.Getenv("CONTENT_TYPE")

	queryParams, _ := url.ParseQuery(queryString)

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

	message := ""

	// Handle actions
	if action == "clear" {
		destroySession(sessionID)
		message = "Session data cleared!"
	}

	// Load session data (after potential clear)
	sessionData := loadSession(sessionID)

	if action == "save" {
		if val := formData["name"]; val != "" {
			sessionData["name"] = val
		}
		if val := formData["message"]; val != "" {
			sessionData["message"] = val
		}
		saveSession(sessionID, sessionData)
		message = "Data saved!"
	}

	// Print headers
	fmt.Println("Cache-Control: no-cache")
	fmt.Printf("Set-Cookie: GOSESSID=%s; Path=/; Max-Age=%d\n", sessionID, sessionTimeout)
	fmt.Println("Content-Type: text/html")
	fmt.Println("")

	// Print page
	name := escapeHTML(sessionData["name"])
	msg := escapeHTML(sessionData["message"])

	fmt.Println(`<!DOCTYPE html>
<html>
<head><title>Go State Demo</title></head>
<body>
<h1>Go State Demo</h1>`)

	if message != "" {
		fmt.Printf("<p><strong>%s</strong></p>\n", message)
	}

	if name != "" || msg != "" {
		fmt.Println("<h3>Saved Data:</h3>")
		if name != "" {
			fmt.Printf("<p>Name: %s</p>\n", name)
		}
		if msg != "" {
			fmt.Printf("<p>Message: %s</p>\n", msg)
		}
		fmt.Println("<hr>")
	}

	fmt.Printf(`<form action='/hw2/go/state-go.cgi' method='POST'>
<input type='hidden' name='action' value='save'>
<label>Name <input type='text' name='name' value='%s'></label>
<br><br>
<label>Message <input type='text' name='message' value='%s'></label>
<br><br>
<button type='submit'>Save</button>
</form>

<br>
<form action='/hw2/go/state-go.cgi' method='POST'>
<input type='hidden' name='action' value='clear'>
<button type='submit'>Clear Data</button>
</form>

</body>
</html>`, name, msg)
}
