<?php
$team = "Victoria, Ryan, and Christine";
$language = "PHP";
$time = date('c');
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

header('Content-Type: text/html; charset=utf-8');
?>
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Hello HTML (PHP)</title>
</head>
<body>
    <h1>Hello from <?= $team ?></h1>
    <ul>
        <li>Language: <?= $language ?></li>
        <li>Generated at: <?= $time ?></li>
        <li>Your IP: <?= $ip ?></li>
    </ul>
</body>
</html>
