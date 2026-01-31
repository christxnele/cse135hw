package main

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

func main() {
	fmt.Println("Cache-Control: no-cache\n")
	fmt.Println("Content-type: application/json\n")

	date := time.Now().Format("Mon Jan 2 15:04:05 2006")
	address := os.Getenv("REMOTE_ADDR");

	message := map[string]string{
		"title": "Hello, Go!",
		"heading": "Hello, Go!",
		"message": "This page was generated with the Go Programming language",
		"time": date,
		"IP": address,
	}

	jsonData, err:= json.Marshal(message)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(jsonData))

}
