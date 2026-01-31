package main

import (
	"os"
	"fmt"
	"time"
)

func main() {
	fmt.Println("Content-Type: text/plain")
	fmt.Println("")

	fmt.Println("Environment variables (Go)")
	fmt.Printf("Generated at: %s\n\n", time.Now().Format(time.RFC3339))

	for _, env := range os.Environ() {
		fmt.Println(env)
	}
}