<?php
header("Cache-Control: no-cache");
header("Content-Type: text/html; charset=utf-8");

$cookie_name = "hw2_state_php";

// Save state
if ($_SERVER["REQUEST_METHOD"] === "POST") {
  $name = $_POST["name"] ?? "";
  $message = $_POST["message"] ?? "";

  $value = $name . "|" . $message;

  setcookie($cookie_name, $value, time() + 3600, "/");
  header("Location: state-view-php.php");
  exit;
}
?>
<!doctype html>
<html lang="en">
<head>
    <title>PHP State Demo - Save</title>
</head>
<body>
    <h1>PHP State Demo - Save</h1>

    <form method="POST">
        <label>Name<input type="text" name="name" required></label>
        <br><br>

        <label>Message<input type="text" name="message" required></label>
        <br><br>

        <button type="submit">Save</button>
    </form>

    <p><a href="state-view-php.php">View saved data</a></p>
</body>
</html>
