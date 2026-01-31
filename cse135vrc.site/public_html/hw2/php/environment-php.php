<?php
header('Content-Type: text/plain; charset=utf-8');

echo "Environment variables (PHP)\n";
echo "Generated at: " . date('c') . "\n\n";

foreach ($_SERVER as $key => $value) {
    if (is_array($value)) {
        $value = json_encode($value);
    }
    echo $key . "=" . $value . "\n";
}
