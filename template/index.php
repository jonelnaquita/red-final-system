<?php

    require 'functions.php';
    $uri = parse_url($_SERVER['REQUEST_URI'])['path'];

    $routes = [
        '/' => '/template/pages/Login.php',
        '/login' => '/template/pages/Login.php',
        '/home' => '/template/pages/Dashboard.php',
        '/manage' => '/template/pages/DataSource.php',
        '/adddata' => '/template/pages/AddDataSource.php',
        '/guidelines' => '/template/pages/UserGuidelines.php',
        '/settings' => '/template/pages/Settings.php'
    ];

    function abort($code = 404){
        http_response_code($code);
        require '/template/pages/404Page.php';

        die();
    }

    if (array_key_exists($uri, $routes)){
        require $routes[$uri];
    }else{
        abort();
    }
?>