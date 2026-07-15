-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 15-07-2026 a las 22:11:41
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `cartasBD`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cartasTbd`
--

CREATE TABLE `cartasTbd` (
  `id` int(11) NOT NULL,
  `numero` int(11) NOT NULL,
  `imagen` varchar(255) NOT NULL,
  `cantidad_mazo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `cartasTbd`
--

INSERT INTO `cartasTbd` (`id`, `numero`, `imagen`, `cantidad_mazo`) VALUES
(1, 1, 'cartas/Pelusa_1.jpg', 13),
(2, 2, 'cartas/Pelusa_2.jpg', 13),
(3, 3, 'cartas/Pelusa_3.jpg', 13),
(4, 4, 'cartas/Pelusa_4.jpg', 13),
(5, 5, 'cartas/Pelusa_5.jpg', 13),
(6, 6, 'cartas/Pelusa_6.jpg', 9),
(7, 7, 'cartas/Pelusa_7.jpg', 9),
(8, 8, 'cartas/Pelusa_8.jpg', 9),
(9, 9, 'cartas/Pelusa_9.jpg', 9),
(10, 10, 'cartas/Pelusa_10.jpg', 9);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cartasTbd`
--
ALTER TABLE `cartasTbd`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `cartasTbd`
--
ALTER TABLE `cartasTbd`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
