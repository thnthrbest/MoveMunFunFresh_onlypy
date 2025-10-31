<?php
    require 'connect.php';
    $user_id = $_POST['user_id'];
    
    $sql = "select * from user where user_id = '$user_id'";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);

    if($count > 0)
    {
        $row = mysqli_fetch_array($result);
        $user_id = $row['user_id'];
        $username = $row['username'];
        echo "$user_id:$username";
    }
    else
    {
        echo "0";
    }
?>