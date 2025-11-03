-- phpMyAdmin SQL Dump
-- version 4.6.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 03, 2025 at 01:04 PM
-- Server version: 5.7.12-log
-- PHP Version: 5.6.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `movemunfunfresh`
--

-- --------------------------------------------------------

--
-- Table structure for table `child`
--

CREATE TABLE `child` (
  `child_id` int(11) NOT NULL,
  `child_name` varchar(50) NOT NULL,
  `child_nickname` char(10) NOT NULL,
  `child_weight` double NOT NULL,
  `child_height` double NOT NULL,
  `child_age` tinyint(4) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `child`
--

INSERT INTO `child` (`child_id`, `child_name`, `child_nickname`, `child_weight`, `child_height`, `child_age`, `user_id`) VALUES
(1, 'ด.ช. กิตติทัต ผิวบาง', 'ต้นกล้า', 14, 101, 6, 1),
(2, 'ด.ช. สงกรานต์  ศรีรักษ์', 'เฮง เฮง', 20.8, 113, 6, 1),
(3, 'ด.ช. ติณณภพ  เกษจันทร์', 'หมากขุน', 18.1, 113, 6, 1),
(4, 'ด.ช. อชิตพล  บุญสร้าง', 'มาร์ช', 18.6, 109, 6, 1),
(5, 'ด.ช. อนาวิล  ตุ้ยรอด', 'ออโต้', 25.4, 118, 6, 1),
(6, 'ด.ช. วันนิด ชัย', 'วันนิด', 19.1, 112, 6, 1),
(7, 'ด.ช. ชัชนันท์ รื่นสุข', 'กันต์', 16.4, 109, 6, 1),
(8, 'ด.ช. ธนเทพ  นิยมทอง', 'บีม', 21.6, 109, 6, 1),
(9, 'ด.ญ. กานต์มณิฐา สิงห์ธรรม', 'ข้าวปุ้น', 15.4, 105, 6, 1),
(10, 'ด.ญ. ธัญชนก  วงศ์กำปั่น', 'ปักเป้า', 25.7, 117, 6, 1),
(11, 'ด.ญ. ฐิติกาญจน์ จันทนา', 'ใบเฟิร์น', 14.6, 106, 6, 1),
(12, 'ด.ญ. น้ำฟ้า', 'น้ำฟ้า', 22.8, 117, 6, 1),
(13, 'ด.ญ. กุลภัสสร์ รัตนถาวร', 'ออนิว', 14.2, 106, 6, 1),
(14, 'ด.ญ. ปวีณ์สุดา  พิมที', 'มีสุข', 14.6, 108, 6, 1),
(15, 'ด.ญ. กมลพร  ผ่องวิถี', 'โมบาย', 19, 112, 6, 1),
(16, 'ด.ญ. เหมยลี่', 'เหมยลี่', 18.2, 109, 6, 1),
(17, 'ด.ญ. วรัญญา สิงห์บ้านหมอ', 'นาเดียร์', 14.2, 100, 6, 1),
(18, 'ด.ญ. ชีวารัตน์  บุญเชียง', 'แทนใจ', 24.4, 112, 6, 1),
(19, 'ด.ญ. กัญญาวีร์ แตงอ่อน', 'อะตอม', 16, 109, 6, 1);

-- --------------------------------------------------------

--
-- Table structure for table `game`
--

CREATE TABLE `game` (
  `game_id` int(11) NOT NULL,
  `game_name` text NOT NULL,
  `game_description` text NOT NULL,
  `part1` tinyint(4) NOT NULL,
  `part2` tinyint(4) NOT NULL,
  `part3` tinyint(4) NOT NULL,
  `part4` tinyint(4) NOT NULL,
  `part5` tinyint(4) NOT NULL,
  `time_spent_playing` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `game`
--

INSERT INTO `game` (`game_id`, `game_name`, `game_description`, `part1`, `part2`, `part3`, `part4`, `part5`, `time_spent_playing`) VALUES
(1, 'สนุกกับเงา', 'เกมที่จะมอบความสนุกให้กับเด้กผ่านการคิดและทำมือเลียนแบบเงาของสัตว์ต่าง', 0, 0, 0, 0, 3, 2),
(2, 'กำแพงหรรษา', 'เกมที่จะให้เด็กได้ขยับร่างกายในท่าทงต่างๆเพื่อหลบเลี่ยงเหล่ากำแพง', 1, 2, 1, 2, 0, 2),
(3, 'ท้าสมองประลองควิซ', 'เกมประชัญปัญญาสมองเหล่าเด็กๆจะต้องคิดคำตอบของคำถามให้ออกเพื่อให้รู้ว่าผิดหรือถูก', 0, 2, 2, 0, 0, 3),
(4, 'มือปราบยุงลาย', 'ยุงลายมาแล้วตบมันเร็ว!!! เดี๋ยวไม่ใช่สินี้มันระเบิด', 2, 2, 2, 0, 2, 2);

-- --------------------------------------------------------

--
-- Table structure for table `play`
--

CREATE TABLE `play` (
  `play_id` int(11) NOT NULL,
  `play_date` date NOT NULL,
  `game_id` int(11) NOT NULL,
  `child_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `rank`
--

CREATE TABLE `rank` (
  `rank_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `child_id` int(11) NOT NULL,
  `score` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL,
  `id` text NOT NULL,
  `username` varchar(50) NOT NULL,
  `classroom` char(4) NOT NULL,
  `password` varchar(25) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`user_id`, `id`, `username`, `classroom`, `password`) VALUES
(1, '1', 'ครูยุ้ย', '3/2', '1');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `child`
--
ALTER TABLE `child`
  ADD PRIMARY KEY (`child_id`);

--
-- Indexes for table `game`
--
ALTER TABLE `game`
  ADD PRIMARY KEY (`game_id`);

--
-- Indexes for table `play`
--
ALTER TABLE `play`
  ADD PRIMARY KEY (`play_id`);

--
-- Indexes for table `rank`
--
ALTER TABLE `rank`
  ADD PRIMARY KEY (`rank_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `child`
--
ALTER TABLE `child`
  MODIFY `child_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;
--
-- AUTO_INCREMENT for table `game`
--
ALTER TABLE `game`
  MODIFY `game_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `play`
--
ALTER TABLE `play`
  MODIFY `play_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `rank`
--
ALTER TABLE `rank`
  MODIFY `rank_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
