<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        #preloader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .loading-icon {
            width: 64px; /* Set the width and height of your icon */
            height: 64px;
            display: flex;
            margin-left: 20px;
        }

        /* Customize the jumping dots loader here */
        .jumping-dots-loader {
            display: inline-block;
            text-align: center;
            font-size: 28px;
        }

        .jumping-dots-loader span{
            background-color: #CE1E2D;
        }

        @keyframes jumping-dots {
            0%, 20%, 80%, 100% {
            transform: translateY(0);
            }
            40% {
            transform: translateY(-10px);
            }
            60% {
            transform: translateY(-5px);
            }
        }
    </style>
</head>
<body>
    <div id="preloader">
        <div class="jumping-dots-loader">
            <img src="../assets/images/RED_Logo.png" class="loading-icon">
            <span></span><span></span><span></span>
        </div>
    </div>
</body>

<script>
  // Hide the preloader once the page is fully loaded
  window.addEventListener('load', function() {
    const preloader = document.getElementById('preloader');
    preloader.style.display = 'none';
  });
</script>

</html>