<?php
    require 'connect.php';
    date_default_timezone_set('Asia/Bangkok');
    $daytime = isset($_POST['play_date']) ? $_POST['play_date'] : date("Y-m-d");
    $child_id = $_POST['child_id'];
    $game_id = $_POST['game_id'];
    $score = $_POST['score'];
    $sql = "INSERT INTO play (child_id, play_date, game_id) VALUES ('$child_id', '$daytime', '$game_id')";
    $result = mysqli_query($db, $sql);
    $sql = "SELECT * FROM rank WHERE game_id = '$game_id' ORDER BY score";
    $result = mysqli_query($db, $sql);
    $row = mysqli_fetch_array($result);
    $score1 = $row['score'];
    $rank_id = $row['rank_id'];
    if($score > $score1)
    {
        $sql = "UPDATE rank SET score = '$score', child_id = '$child_id' WHERE rank_id = '$rank_id'";
        $result = mysqli_query($db, $sql);
    }
    $sql = "SELECT * FROM play WHERE child_id = '$child_id' AND play_date = '$daytime'";
    $result = mysqli_query($db, $sql);
    $count = mysqli_num_rows($result);
    $sum1 = 0 ; $sum2 = 0 ; $sum3 = 0 ; $sum4 = 0 ; $sum5 = 0 ;
    for($i=1;$i <= $count;$i++)
    {
        $row = mysqli_fetch_array($result);
        $game_id = $row['game_id'];
        $sql2 = "SELECT * FROM game WHERE game_id = '$game_id'";
        $result2 = mysqli_query($db, $sql2);
        $row2 = mysqli_fetch_array($result2);
        $sum1 += $row2['part1'];
        $sum2 += $row2['part2'];
        $sum3 += $row2['part3'];
        $sum4 += $row2['part4'];
        $sum5 += $row2['part5'];
    }
    echo "$sum1:$sum2:$sum3:$sum4:$sum5";
?>