package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/url"
	"os"
	"strings"
	"time"
)

func main() {
	fmt.Println("Content-Type: application/json")
	fmt.Println("")

	/* get request info from env */
	method := os.Getenv("REQUEST_METHOD")
	contentType := os.Getenv("CONTENT_TYPE")
	queryString := os.Getenv("QUERY_STRING")

	data := make(map[string]string)

	if method == "GET" {
		/* parse query string */
		values, _ := url.ParseQuery(queryString)
		for key, val := range values {
			data[key] = val[0]
		}
	} else {
		// POST
		body, _ := io.ReadAll(os.Stdin)
		if strings.Contains(contentType, "application/json") {
			// JSON body
			json.Unmarshal(body, &data)
		} else {
			// form data
			values, _ := url.ParseQuery(string(body))
			for key, val := range values {
				data[key] = val[0]
			}
		}
	}

	// building response
	response := map[string]interface{}{
		"language": "Go",
		"method": method,
		"time": time.Now().Format(time.RFC3339),
		"ip":            os.Getenv("REMOTE_ADDR"),
		"user_agent":    os.Getenv("HTTP_USER_AGENT"),
		"data_received": data,

	}

	// output JSON
	jsonData, _ := json.Marshal(response)
	fmt.Println(string(jsonData))
}