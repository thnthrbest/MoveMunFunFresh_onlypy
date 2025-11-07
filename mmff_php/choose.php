<?php
    require 'connect.php';
    $user_id = $_POST['user_id'];

    $sql = "SELECT * FROM child WHERE user_id = '$user_id'";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);

    if($count > 0)
    {
        for($i=1;$i<=$count;$i++)
        {
            if($i<=$count) echo "#";
            $row = mysqli_fetch_array($result);
            $child_id = $row['child_id'];
            $child_nickname = $row['child_nickname'];

            echo "$child_id:$child_nickname";
        }
    }
    else echo "0";
?>