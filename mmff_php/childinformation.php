<?php
    require 'connect.php';
    //$user_id = $_POST['user_id'];
    $user_id = "1";

    $sql = "SELECT * FROM child WHERE user_id = '$user_id'";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);

    if($count > 0)
    {
        for($i=1;$i<=$count;$i++)
        {
            if($i<$count) echo "#";
            $row = mysqli_fetch_array($result);
            $child_name = $row['child_name'];
            $child_nickname = $row['child_nickname'];
            $child_weight = $row['child_weight'];
            $child_height = $row['child_height'];
            $child_age = $row['child_age'];

            echo "$child_name:$child_nickname:$child_weight:$child_height:$child_age";
        }
    }
    else echo "0";
?>