<?php
    require 'connect.php';
    $child_id = $_POST['child_id'];

    $sql = "SELECT * FROM child WHERE child_id = $child_id";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);

    if($count > 0)
    {
        $row = mysqli_fetch_array($result);
        $child_name = $row['child_name'];
        $child_nickname = $row['child_nickname'];
        $child_weight = $row['child_weight'];
        $child_height = $row['child_height'];
        $child_age = $row['child_age'];
        echo "$child_name:$child_nickname:$child_weight:$child_height:$child_age";
    }
    else echo "0";
?>