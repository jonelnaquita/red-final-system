<?php include './components/preloader.php';?>
<!DOCTYPE html>
<html lang="en">

<head>
  <!-- Required meta tags -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>RED Login Page</title>
  <!-- plugins:css -->
  <link rel="stylesheet" href="vendors/feather/feather.css">
  <link rel="stylesheet" href="vendors/mdi/css/materialdesignicons.min.css">
  <link rel="stylesheet" href="vendors/ti-icons/css/themify-icons.css">
  <link rel="stylesheet" href="vendors/typicons/typicons.css">
  <link rel="stylesheet" href="vendors/simple-line-icons/css/simple-line-icons.css">
  <link rel="stylesheet" href="vendors/css/vendor.bundle.base.css">
  <link rel="stylesheet" href="css/vertical-layout-light/style.css">
  <link rel="stylesheet" href="css/custom/login.css">

  <link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.0/css/line.css">
  
  <link rel="shortcut icon" href="../assets/images/RED_Logo.png" />

  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css">

  <!-- plugins:js -->
  <script src="../vendors/js/vendor.bundle.base.js"></script>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
  <script>
    toastr.options = {
      "closeButton": true,
      "debug": true,
      "newestOnTop": false,
      "progressBar": false,
      "positionClass": "toast-top-right",
      "preventDuplicates": false,
      "onclick": null,
      "showDuration": "300",
      "hideDuration": "1000",
      "timeOut": "5000",
      "extendedTimeOut": "1000",
      "showEasing": "swing",
      "hideEasing": "linear",
      "showMethod": "fadeIn",
      "hideMethod": "fadeOut"
    }
  </script>
</head>

<?php
require 'vendor/autoload.php'; // Include the MongoDB PHP driver
require 'config/mongodbConn.php';

// MongoDB connection parameters

$collectionName = "user"; // Replace with your collection name

// Create a MongoDB client
$client = new MongoDB\Client($connectionString);

// Select the database and collection
$database = $client->$databaseName;
$collection = $database->$collectionName;

ob_start(); // Start output buffering

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Retrieve form inputs
    $username = $_POST["username"];
    $password = $_POST["password"];

    // Find the user in the collection by email
    $user = $collection->findOne(["email" => $username]);

    if ($user) {
        // User email exists in the database, now check the password
        if (password_verify($password, $user["password"])) {
            // Password is correct
            $_SESSION["user_id"] = $user["_id"]; // Store user's ObjectId in the session
            header("Location: /home");
            exit();
        } else {
            // Password is incorrect
            echo "<script>toastr.error('Password is incorrect!');</script>";
        }
    } else {
        // Email not found in the database
        echo "<script>toastr.error('Email not found in the database.');</script>";
    }
}

ob_end_flush(); // End and flush the output buffer
?>


<body>
  <div class="container-scroller">
    <div class="container-fluid page-body-wrapper full-page-wrapper">
      <div class="content-wrapper d-flex align-items-center auth px-0">
        <div class="row w-100 mx-0">
          <div class="col-lg-4 mx-auto">
            <div class="auth-form-light text-left py-5 px-4 px-sm-5">
              <div class="brand-logo">
                <img src="../assets/images/RED_Logo.png" alt="logo">
              </div>
              <h4>Hello, I'm RED! Let's get started</h4>
              <h6 class="fw-light">Sign in to continue.</h6>
              <form class="pt-3" method="POST">
                <div class="form-group">
                    <input type="email" class="form-control form-control-lg" name="username" id="exampleInputEmail1" placeholder="Username">
                </div>
                <div class="input-with-toggle">
                    <input type="password" class="form-control form-control-lg" name="password" id="inputPassword" placeholder="Password">
                    <i class="uil uil-eye-slash toggle" id="togglePassword"></i>
                </div>

                <div class="mt-3">
                    <button type="submit" class="btn btn-block btn-primary btn-lg font-weight-medium auth-form-btn">SIGN IN</button>
                </div>
                <div class="my-2 d-flex justify-content-between align-items-center">
                    <p></p>
                    <a href="#" class="auth-link text-black">Forgot password?</a>
                </div>
            </form>
            </div>
          </div>
        </div>
      </div>
      <!-- content-wrapper ends -->
    </div>
    <!-- page-body-wrapper ends -->
  </div>
  <!-- container-scroller -->
  <!-- plugins:js -->
  <script src="../../vendors/js/vendor.bundle.base.js"></script>
  <!-- endinject -->
  <!-- Plugin js for this page -->
  <script src="../../vendors/bootstrap-datepicker/bootstrap-datepicker.min.js"></script>
  <!-- End plugin js for this page -->
  <!-- inject:js -->
  <script src="../../js/off-canvas.js"></script>
  <script src="../../js/hoverable-collapse.js"></script>
  <script src="../../js/template.js"></script>
  <script src="../../js/settings.js"></script>
  <script src="../../js/todolist.js"></script>
  <script src="../vendors/js/vendor.bundle.base.js"></script>
  <!-- endinject -->
</body>

<script>
    const passwordInput = document.getElementById("inputPassword");
    const toggleButton = document.getElementById("togglePassword");

    toggleButton.addEventListener("click", function () {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            toggleButton.classList.remove("uil-eye-slash");
            toggleButton.classList.add("uil-eye");
        } else {
            passwordInput.type = "password";
            toggleButton.classList.remove("uil-eye");
            toggleButton.classList.add("uil-eye-slash");
        }
    });
</script>
</html>
