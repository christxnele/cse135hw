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
		if strings.HasPrefix(part, "go_session_id=") {
			return strings.TrimPrefix(part, "go_session_id=")
		}
	}
	return ""
}

func getSessionFilePath(sessionID string) string {
	return sessionDir + "/session_" + sessionID + ".json"
}

func loadSession(sessionID string) map[string]string {
	data := make(map[string]string)
	if sessionID == "" {
		return data
	}
	content, err := os.ReadFile(getSessionFilePath(sessionID))
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

func clearSession(sessionID string) {
	if sessionID != "" {
		os.Remove(getSessionFilePath(sessionID))
	}
}

func main() {
	method := os.Getenv("REQUEST_METHOD")
	queryString := os.Getenv("QUERY_STRING")
	contentType := os.Getenv("CONTENT_TYPE")

	// Parse query params
	queryParams, _ := url.ParseQuery(queryString)
	action := queryParams.Get("action")

	// Get or create session ID
	sessionID := getSessionIDFromCookie()
	isNewSession := sessionID == ""
	if isNewSession {
		sessionID = generateSessionID()
	}

	// Load existing session data
	sessionData := loadSession(sessionID)

	// Handle POST data
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

	// Process actions
	message := ""
	switch action {
	case "save":
		// Save form data to session
		for key, val := range formData {
			if key != "action" && val != "" {
				sessionData[key] = val
			}
		}
		saveSession(sessionID, sessionData)
		message = "Data saved successfully!"

	case "clear":
		clearSession(sessionID)
		sessionData = make(map[string]string)
		message = "Session cleared!"

	case "view":
		message = "Current session data:"

	default:
		message = "State Management Demo (Go)"
	}

	// Output headers
	fmt.Println("Content-Type: application/json")
	if isNewSession {
		// Set cookie with session ID (expires in 1 hour)
		expires := time.Now().Add(time.Hour).UTC().Format(time.RFC1123)
		fmt.Printf("Set-Cookie: go_session_id=%s; Path=/; Expires=%s\n", sessionID, expires)
	}
	fmt.Println("")

	// Build response
	response := map[string]interface{}{
		"language":   "Go",
		"action":     action,
		"message":    message,
		"session_id": sessionID,
		"time":       time.Now().Format(time.RFC3339),
		"data":       sessionData,
	}

	jsonData, _ := json.MarshalIndent(response, "", "  ")
	fmt.Println(string(jsonData))
}
