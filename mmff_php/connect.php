<?php
    $server = "localhost"; 
    $user="root"; 
    $pass="12345678"; 
    $database="movemunfunfresh"; 
    $db = mysqli_connect($server,$user,$pass,$database);

    if(mysqli_connect_error())
    {
        die("". mysqli_connect_error());
    }
?>