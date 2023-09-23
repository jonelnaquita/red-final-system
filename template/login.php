
<!DOCTYPE html>
<html lang="en">

<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>RED Login Page</title>
    <!-- plugins:css -->
    <link rel="stylesheet" href="static/vendors/feather/feather.css">
    <link rel="stylesheet" href="static/vendors/mdi/css/materialdesignicons.min.css">
    <link rel="stylesheet" href="static/vendors/ti-icons/css/themify-icons.css">
    <link rel="stylesheet" href="static/vendors/typicons/typicons.css">
    <link rel="stylesheet" href="static/vendors/simple-line-icons/css/simple-line-icons.css">
    <link rel="stylesheet" href="static/vendors/css/vendor.bundle.base.css">
    <link rel="stylesheet" href="static/css/vertical-layout-light/style.css">
    <link rel="stylesheet" href="static/css/custom/login.css">

    <link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.0/css/line.css">
    
    <link rel="shortcut icon" href="static/assets/images/RED_Logo.png" />

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css">
    <link rel="stylesheet" href="static/css/custom/preloader.css">


    <!-- plugins:js -->
    <script src="static/vendors/js/vendor.bundle.base.js"></script>

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

<body>
    <!--Preloader-->
    <div id="preloader">
        <div class="jumping-dots-loader">
            <img src="static/assets/images/RED_Logo.png" class="loading-icon">
            <span></span><span></span><span></span>
        </div>
    </div>

    <div class="container-scroller">
        <div class="container-fluid page-body-wrapper full-page-wrapper">
        <div class="content-wrapper d-flex align-items-center auth px-0">
            <div class="row w-100 mx-0">
            <div class="col-lg-4 mx-auto">
                <div class="auth-form-light text-left py-5 px-4 px-sm-5">
                <div class="brand-logo">
                    <img src="static/assets/images/RED_Logo.png" alt="logo">
                </div>
                <h4>Hello, I'm RED! Let's get started</h4>
                <h6 class="fw-light">Sign in to continue.</h6>
                <h6><?php echo "Erorrrrrr!" ?></h6>
                <form class="pt-3" action="{{ url_for('login') }}" method="POST">
                    {% if message is defined and message %}
                        <script>
                            toastr.error('{{ message }}');
                        </script>
                    {% endif %}

                    <div class="form-group">
                        <input type="email" class="form-control form-control-lg" name="email" id="exampleInputEmail1" placeholder="Username">
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
  <script src="static/vendors/js/vendor.bundle.base.js"></script>
  <!-- endinject -->
  <!-- Plugin js for this page -->
  <script src="static/vendors/bootstrap-datepicker/bootstrap-datepicker.min.js"></script>
  <!-- End plugin js for this page -->
  <!-- inject:js -->
  <script src="static/js/off-canvas.js"></script>
  <script src="static/js/hoverable-collapse.js"></script>
  <script src="static/js/template.js"></script>
  <script src="static/js/settings.js"></script>
  <script src="static/js/todolist.js"></script>
  <script src="static//vendors/js/vendor.bundle.base.js"></script>

  <script src="static/js/preloader.js"></script>
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
