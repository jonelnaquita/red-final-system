<?php
$rowToDelete = $_POST['rowToDelete'];

$csvFile = "../files/faq_sheet.csv";
$fileContent = file($csvFile);
$updatedContent = '';

foreach ($fileContent as $lineNumber => $line) {
    if ($lineNumber !== $rowToDelete) {
        $updatedContent .= $line;
    }
}

file_put_contents($csvFile, $updatedContent);

echo "Success";
?>
