<?php
header("Cache-Control: no-cache");
header("Content-Type: text/html; charset=utf-8");

$cookie_name = "hw2_state_php";

// Clear state
if (isset($_GET["clear"]) && $_GET["clear"] === "1") {
  setcookie($cookie_name, "", time() - 3600, "/");
  header("Location: state-view-php.php");
  exit;
}

$name = "";
$message = "";

if (isset($_COOKIE[$cookie_name])) {
    [$name, $message] = explode("|", $_COOKIE[$cookie_name], 2);
}
?>
<!doctype html>
<html lang="en">
<head>
  <title>PHP State Demo - View</title>
</head>
<body>

<h1>PHP State Demo - View</h1>

<p>
  <strong>Name:</strong>
  <?= $name === "" ? "<em>(none)</em>" : htmlspecialchars($name) ?>
</p>

<p>
  <strong>Message:</strong>
  <?= $message === "" ? "<em>(none)</em>" : htmlspecialchars($message) ?>
</p>

<p><a href="state-php.php">Back to save</a></p>
<p><a href="state-view-php.php?clear=1">Clear saved data</a></p>

</body>
</html>
