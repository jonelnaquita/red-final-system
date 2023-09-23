<?php
    include 'components/header.php';
    include 'components/preloader.php'
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
<div class="container-scroller">
    <?php include 'components/navbar.php'; ?>
    <div class="container-fluid page-body-wrapper">
        <?php include 'components/sidebar.php'; ?>
        <div class="main-panel">
            <div class="card">
                <div class="card-body">
                    <h2 class="mb-2">SETTINGS</h2>
                    <ul class="nav nav-tabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button type="button"
                                id="uncontrolled-tab-example-tab-profile"
                                role="tab" data-rr-ui-event-key="profile"
                                aria-controls="uncontrolled-tab-example-tabpane-profile"
                                aria-selected="false"
                                class="nav-link active">
                                Change Email
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button type="button"
                                id="uncontrolled-tab-example-tab-contact"
                                role="tab"
                                data-rr-ui-event-key="contact"
                                aria-controls="uncontrolled-tab-example-tabpane-contact"
                                aria-selected="false"
                                class="nav-link"
                                tabindex="-1">
                                Change Password
                            </button>
                        </li>
                    </ul>
                    <div class="tab-content">
                        <div role="tabpanel" id="uncontrolled-tab-example-tabpane-profile" aria-labelledby="uncontrolled-tab-example-tab-profile" class="fade test-tab tab-pane active show">
                            <div class="card-body">
                                <h4 class="card-title">Change Email</h4>
                                <p class="card-description">Update your email address</p>
                                <form class="forms-sample">
                                    <div class="form-group">
                                        <label for="exampleInputUsername1">Current Email Address</label>
                                        <input type="email" id="exampleInputUsername1" class="form-control">
                                    </div>
                                    <div class="form-group">
                                        <label for="exampleInputEmail1">New Email Address</label>
                                        <input type="email" id="exampleInputEmail1" class="form-control">
                                    </div>
                                    <div class="form-group">
                                        <label>Enter your password</label>
                                        <input type="password" class="form-control" value="">
                                    </div>
                                    <button type="submit" class="btn btn-danger me-2">Update Email</button>
                                </form>
                            </div>
                        </div>
                        <div role="tabpanel" id="uncontrolled-tab-example-tabpane-contact" aria-labelledby="uncontrolled-tab-example-tab-contact" class="fade tab-pane">
                            <div class="card-body">
                                <h4 class="card-title">Change Password</h4>
                                <p class="card-description">Update your password</p>
                                <form class="forms-sample">
                                    <div class="form-group">
                                        <label for="exampleInputOldPassword">Current Password</label>
                                        <input type="password" id="exampleInputOldPassword" class="form-control">
                                    </div>
                                    <div class="form-group">
                                        <label for="exampleInputNewPassword">New Password</label>
                                        <input type="password" id="exampleInputNewPassword" class="form-control">
                                    </div>
                                    <div class="form-group">
                                        <label for="eexampleInputConfirmPassword">Re-enter your password</label>
                                        <input type="password" class="form-control" value="" for="exampleInputConfirmPassword">
                                    </div>
                                    <button type="submit" class="btn btn-danger me-2">Update Password</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            
            </div>
        </div>
    </div>
    <?php include 'components/footer.php'; ?>
</div>
</body>

<script>
    // Get all the tab buttons and tab panes
    const tabButtons = document.querySelectorAll('.nav-tabs button');
    const tabPanes = document.querySelectorAll('.tab-content .tab-pane');

    // Add click event listener to each tab button
    tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Get the data-rr-ui-event-key attribute value of the clicked button
        const targetTab = button.getAttribute('data-rr-ui-event-key');

        // Hide all tab panes
        tabPanes.forEach(pane => {
        pane.classList.remove('active', 'show');
        });

        // Show the corresponding tab pane
        const activePane = document.getElementById('uncontrolled-tab-example-tabpane-' + targetTab);
        if (activePane) {
        activePane.classList.add('active', 'show');
        }

        // Update the "aria-selected" attribute for the tab buttons
        tabButtons.forEach(btn => {
        const isActive = btn === button;
        btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
        btn.classList.toggle('active', isActive);
        });
    });
    });
</script>
</html>