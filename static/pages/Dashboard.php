<?php
    include 'components/header.php';
    include 'config/session.php';
    
    if (!isUserLoggedIn()) {
        redirectToLogin(); // Redirect to the login page if not logged in
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<div class="container-scroller">
    <?php include 'components/navbar.php'; ?>
    <div class="container-fluid page-body-wrapper">
        <?php include 'components/sidebar.php'; ?>
        <div class="main-panel">

        </div>
    </div>
    <?php include 'components/footer.php'; ?>
</div>
</body>
</html>