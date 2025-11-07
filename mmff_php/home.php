<?php
    require 'connect.php';

    $sql="select * from student"; 
    $result = mysqli_query($db,$sql); 
    $count = mysqli_num_rows($result); 
    for($i=1;$i<=$count;$i++){
        $row = mysqli_fetch_array($result); 
        $name = $row['name'];  
        $class = $row['class'];    
        $phone = $row['phone_number']; 
        echo "$name # $class # $phone <br> " ;
    }
?>