<?php
    require 'connect.php';
    
    $id =$_POST['id'];
    $password = $_POST['password'];

    $sql="select * FROM user WHERE id = '$id' AND password ='$password'";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);
    if($count > 0)
    {
            $row = mysqli_fetch_array($result);
            $user_id = $row['user_id'];
            $username = $row['username'];
            echo "$user_id:$username" ;
    }
    else{
        echo "0";
    }
?>
