package main

import (
	"fmt"
	"time"
	"os"

)

func main() {

	fmt.Println("Cache-Control: no-cache")
	fmt.Println("Content-Type: text/html")
	fmt.Println("") 
	
	fmt.Println("<!DOCTYPE html>")
	fmt.Println("<html>")
	fmt.Println("<head>")
	fmt.Println("<title>Hello CGI World</title>")
	fmt.Println("</head>")
	fmt.Println("<body>")

	fmt.Println("<h1 align=center>Hello HTML World</h1><hr/>")
	fmt.Println("<p>Hello from Victoria Timofeev, Christine Le, and Ryan Soe!</p>")
	fmt.Println("<p>This page was generated with the Go programming langauge</p>")


	date := time.Now().Format("Mon Jan 2 15:04:05 2006")
	fmt.Printf("<p>This program was generated at: %s</p>\n", date)

	/*IP Address is an environment variable when using CGI*/

	address := os.Getenv("REMOTE_ADDR");
	fmt.Printf("<p>Your current IP Address is: %s</p>\n", address)

	fmt.Println("</body>")
	fmt.Println("</html>")
	}