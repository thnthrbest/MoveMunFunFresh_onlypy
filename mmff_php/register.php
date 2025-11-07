<?php
    require 'connect.php';
    $id = $_POST['id'];
    $classroom = $_POST['classroom'];
    $username = $_POST['username'];
    $password = $_POST['password'];

    $sql = "SELECT * FROM user WHERE id = '$id'";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);

    if($count > 0)
    {
        echo "0";
    }
    else
    {
        $sql = "INSERT INTO user (username,password,id,classroom) VALUES ('$username','$password','$id','$classroom')";
        $result = mysqli_query($db, $sql);
    }
?>