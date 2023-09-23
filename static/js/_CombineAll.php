<?php
$jsFiles = glob('/js/*.js');
$combinedJS = '';

foreach ($jsFiles as $file) {
    $combinedJS .= file_get_contents($file);
}

// Set the appropriate content type and output the combined JS
header('Content-Type: application/javascript');
echo $combinedJS;
?>