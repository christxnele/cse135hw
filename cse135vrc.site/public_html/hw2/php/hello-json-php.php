<?php
header('Content-Type: application/json; charset=utf-8');

$data = [
    "team" => "Victoria, Ryan, and Christine",
    "language" => "PHP",
    "generated_at" => date('c'),
    "ip" => $_SERVER['REMOTE_ADDR'] ?? 'unknown'
];

echo json_encode($data);
