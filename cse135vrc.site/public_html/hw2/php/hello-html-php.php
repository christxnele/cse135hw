<?php
header("Cache-Control: no-cache");
header("Content-Type: text/html; charset=utf-8");

$current_time = date("D M d H:i:s Y");
$ip_address = $_SERVER['REMOTE_ADDR'] ?? 'Unknown';
?>
<!DOCTYPE html>
<html>
<head>
    <title>Hello CGI World</title>
</head>
<body>

<h1 align="center">Hello HTML World</h1><hr/>

<p>Hello from Victoria Timofeev, Christine Le, and Ryan Soe!</p>
<p>This page was generated with the PHP programming language</p>
<p>This program was generated at: <?= $current_time ?></p>
<p>Your current IP Address is: <?= $ip_address ?></p>

</body>
</html>
