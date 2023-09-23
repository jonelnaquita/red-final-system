<?php
// Start or resume the session if not already started
if (session_status() == PHP_SESSION_NONE) {
    session_start();
}

if (!function_exists('isUserLoggedIn')) {
    /**
     * Function to check if the user is logged in.
     *
     * @return bool True if the user is logged in, false otherwise.
     */
    function isUserLoggedIn() {
        // Check if the 'user_id' session variable is set
        return isset($_SESSION['user_id']);
    }
}

if (!function_exists('redirectToLogin')) {
    /**
     * Function to redirect the user to the login page if they are not logged in.
     */
    function redirectToLogin() {
        if (!isUserLoggedIn()) {
            header("Location: /login"); // Replace 'login.php' with your login page URL
            exit();
        }
    }
}

// You can define other session-related functions or configuration here as needed.
?>
