<?php
require_once('../config/session.php'); // Include the session.php file

// Destroy the current session
session_destroy();

// Redirect the user to a logout confirmation page or any other page
header("Location: /login"); // Replace with your desired logout confirmation page
exit();
?>
