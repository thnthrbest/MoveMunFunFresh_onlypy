<?php
    require 'connect.php';
    $game_id = $_POST['game_id'];

    $sql = "SELECT * FROM game WHERE game_id = '$game_id'";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);

    if($count > 0)
    {
        $row = mysqli_fetch_array($result);
        $game_name = $row['game_name'];
        $game_description = $row['game_description'];

        echo "$game_name:$game_description";
    }
    else echo "0";
?>