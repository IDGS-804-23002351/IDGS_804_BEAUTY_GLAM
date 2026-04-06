-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: salon_belleza
-- ------------------------------------------------------
-- Server version	8.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bitacora`
--

DROP TABLE IF EXISTS `bitacora`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bitacora` (
  `id_bitacora` int NOT NULL AUTO_INCREMENT,
  `accion` varchar(100) DEFAULT NULL,
  `fecha_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  `tabla_afectada` varchar(100) DEFAULT NULL,
  `id_registro_afectado` int DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  PRIMARY KEY (`id_bitacora`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `bitacora_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitacora`
--

LOCK TABLES `bitacora` WRITE;
/*!40000 ALTER TABLE `bitacora` DISABLE KEYS */;
/*!40000 ALTER TABLE `bitacora` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cita`
--

DROP TABLE IF EXISTS `cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cita` (
  `id_cita` int NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime DEFAULT NULL,
  `estatus` enum('PENDIENTE','CONFIRMADA','CANCELADA','FINALIZADA') DEFAULT 'PENDIENTE',
  `id_cliente` int DEFAULT NULL,
  `id_empleado` int DEFAULT NULL,
  PRIMARY KEY (`id_cita`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_empleado` (`id_empleado`),
  CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cita`
--

LOCK TABLES `cita` WRITE;
/*!40000 ALTER TABLE `cita` DISABLE KEYS */;
/*!40000 ALTER TABLE `cita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  `id_persona` int DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  KEY `id_persona` (`id_persona`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `cliente_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  CONSTRAINT `cliente_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compra_proveedor`
--

DROP TABLE IF EXISTS `compra_proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compra_proveedor` (
  `id_compra_proveedor` int NOT NULL AUTO_INCREMENT,
  `fecha_compra` datetime DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(10,2) DEFAULT NULL,
  `id_proveedor` int DEFAULT NULL,
  PRIMARY KEY (`id_compra_proveedor`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `compra_proveedor_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compra_proveedor`
--

LOCK TABLES `compra_proveedor` WRITE;
/*!40000 ALTER TABLE `compra_proveedor` DISABLE KEYS */;
/*!40000 ALTER TABLE `compra_proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_cita`
--

DROP TABLE IF EXISTS `detalle_cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_cita` (
  `id_detalle_cita` int NOT NULL AUTO_INCREMENT,
  `id_cita` int DEFAULT NULL,
  `id_servicio` int DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  `descuento` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id_detalle_cita`),
  KEY `id_cita` (`id_cita`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `detalle_cita_ibfk_1` FOREIGN KEY (`id_cita`) REFERENCES `cita` (`id_cita`),
  CONSTRAINT `detalle_cita_ibfk_2` FOREIGN KEY (`id_servicio`) REFERENCES `servicio` (`id_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_cita`
--

LOCK TABLES `detalle_cita` WRITE;
/*!40000 ALTER TABLE `detalle_cita` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_cita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_compra`
--

DROP TABLE IF EXISTS `detalle_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_compra` (
  `id_detalle_compra` int NOT NULL AUTO_INCREMENT,
  `id_compra_proveedor` int DEFAULT NULL,
  `codigo_producto` varchar(50) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_detalle_compra`),
  KEY `id_compra_proveedor` (`id_compra_proveedor`),
  KEY `codigo_producto` (`codigo_producto`),
  CONSTRAINT `detalle_compra_ibfk_1` FOREIGN KEY (`id_compra_proveedor`) REFERENCES `compra_proveedor` (`id_compra_proveedor`),
  CONSTRAINT `detalle_compra_ibfk_2` FOREIGN KEY (`codigo_producto`) REFERENCES `producto` (`codigo_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_compra`
--

LOCK TABLES `detalle_compra` WRITE;
/*!40000 ALTER TABLE `detalle_compra` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_pago`
--

DROP TABLE IF EXISTS `detalle_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_pago` (
  `id_detalle_pago` int NOT NULL AUTO_INCREMENT,
  `id_pago` int DEFAULT NULL,
  `id_metodo_pago` int DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_detalle_pago`),
  KEY `id_pago` (`id_pago`),
  KEY `id_metodo_pago` (`id_metodo_pago`),
  CONSTRAINT `detalle_pago_ibfk_1` FOREIGN KEY (`id_pago`) REFERENCES `pago` (`id_pago`),
  CONSTRAINT `detalle_pago_ibfk_2` FOREIGN KEY (`id_metodo_pago`) REFERENCES `metodo_pago` (`id_metodo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_pago`
--

LOCK TABLES `detalle_pago` WRITE;
/*!40000 ALTER TABLE `detalle_pago` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `id_empleado` int NOT NULL AUTO_INCREMENT,
  `fecha_contratacion` date DEFAULT NULL,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  `id_persona` int DEFAULT NULL,
  `id_puesto` int DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  PRIMARY KEY (`id_empleado`),
  KEY `id_persona` (`id_persona`),
  KEY `id_puesto` (`id_puesto`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `empleado_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  CONSTRAINT `empleado_ibfk_2` FOREIGN KEY (`id_puesto`) REFERENCES `puesto` (`id_puesto`),
  CONSTRAINT `empleado_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado_horario`
--

DROP TABLE IF EXISTS `empleado_horario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado_horario` (
  `id_empleado` int NOT NULL,
  `id_horario` int NOT NULL,
  PRIMARY KEY (`id_empleado`,`id_horario`),
  KEY `id_horario` (`id_horario`),
  CONSTRAINT `empleado_horario_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  CONSTRAINT `empleado_horario_ibfk_2` FOREIGN KEY (`id_horario`) REFERENCES `horario` (`id_horario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado_horario`
--

LOCK TABLES `empleado_horario` WRITE;
/*!40000 ALTER TABLE `empleado_horario` DISABLE KEYS */;
/*!40000 ALTER TABLE `empleado_horario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empresa`
--

DROP TABLE IF EXISTS `empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresa` (
  `rfc` varchar(13) NOT NULL,
  `nombre_empresa` varchar(150) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `contacto` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`rfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empresa`
--

LOCK TABLES `empresa` WRITE;
/*!40000 ALTER TABLE `empresa` DISABLE KEYS */;
/*!40000 ALTER TABLE `empresa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_estatus`
--

DROP TABLE IF EXISTS `historial_estatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_estatus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tabla_afectada` varchar(100) NOT NULL,
  `id_registro` int NOT NULL,
  `estatus_anterior` varchar(50) DEFAULT NULL,
  `estatus_nuevo` varchar(50) NOT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_estatus`
--

LOCK TABLES `historial_estatus` WRITE;
/*!40000 ALTER TABLE `historial_estatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_estatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `horario`
--

DROP TABLE IF EXISTS `horario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `horario` (
  `id_horario` int NOT NULL AUTO_INCREMENT,
  `dia` enum('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO') DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  PRIMARY KEY (`id_horario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `horario`
--

LOCK TABLES `horario` WRITE;
/*!40000 ALTER TABLE `horario` DISABLE KEYS */;
/*!40000 ALTER TABLE `horario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumo_servicio`
--

DROP TABLE IF EXISTS `insumo_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumo_servicio` (
  `id_insumo_servicio` int NOT NULL AUTO_INCREMENT,
  `id_servicio` int DEFAULT NULL,
  `codigo_producto` varchar(50) DEFAULT NULL,
  `cantidad_utilizada` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_insumo_servicio`),
  KEY `id_servicio` (`id_servicio`),
  KEY `codigo_producto` (`codigo_producto`),
  CONSTRAINT `insumo_servicio_ibfk_1` FOREIGN KEY (`id_servicio`) REFERENCES `servicio` (`id_servicio`),
  CONSTRAINT `insumo_servicio_ibfk_2` FOREIGN KEY (`codigo_producto`) REFERENCES `producto` (`codigo_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumo_servicio`
--

LOCK TABLES `insumo_servicio` WRITE;
/*!40000 ALTER TABLE `insumo_servicio` DISABLE KEYS */;
/*!40000 ALTER TABLE `insumo_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_producto`
--

DROP TABLE IF EXISTS `inventario_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario_producto` (
  `codigo_producto` varchar(50) NOT NULL,
  `stock_minimo` int DEFAULT '0',
  `stock_maximo` int DEFAULT '0',
  `ultima_actualizacion` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`codigo_producto`),
  CONSTRAINT `inventario_producto_ibfk_1` FOREIGN KEY (`codigo_producto`) REFERENCES `producto` (`codigo_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_producto`
--

LOCK TABLES `inventario_producto` WRITE;
/*!40000 ALTER TABLE `inventario_producto` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventario_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marca`
--

DROP TABLE IF EXISTS `marca`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marca` (
  `id_marca` int NOT NULL AUTO_INCREMENT,
  `nombre_marca` varchar(100) DEFAULT NULL,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  `rfc` varchar(13) DEFAULT NULL,
  PRIMARY KEY (`id_marca`),
  KEY `rfc` (`rfc`),
  CONSTRAINT `marca_ibfk_1` FOREIGN KEY (`rfc`) REFERENCES `empresa` (`rfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marca`
--

LOCK TABLES `marca` WRITE;
/*!40000 ALTER TABLE `marca` DISABLE KEYS */;
/*!40000 ALTER TABLE `marca` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metodo_pago`
--

DROP TABLE IF EXISTS `metodo_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metodo_pago` (
  `id_metodo_pago` int NOT NULL AUTO_INCREMENT,
  `nombre_metodo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_metodo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metodo_pago`
--

LOCK TABLES `metodo_pago` WRITE;
/*!40000 ALTER TABLE `metodo_pago` DISABLE KEYS */;
/*!40000 ALTER TABLE `metodo_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modulo`
--

DROP TABLE IF EXISTS `modulo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modulo` (
  `id_modulo` int NOT NULL AUTO_INCREMENT,
  `nombre_modulo` varchar(100) NOT NULL,
  PRIMARY KEY (`id_modulo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modulo`
--

LOCK TABLES `modulo` WRITE;
/*!40000 ALTER TABLE `modulo` DISABLE KEYS */;
/*!40000 ALTER TABLE `modulo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimiento_inventario`
--

DROP TABLE IF EXISTS `movimiento_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimiento_inventario` (
  `id_movimiento` int NOT NULL AUTO_INCREMENT,
  `codigo_producto` varchar(50) DEFAULT NULL,
  `tipo` enum('ENTRADA','SALIDA','AJUSTE') DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `motivo` varchar(150) DEFAULT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_movimiento`),
  KEY `codigo_producto` (`codigo_producto`),
  CONSTRAINT `movimiento_inventario_ibfk_1` FOREIGN KEY (`codigo_producto`) REFERENCES `producto` (`codigo_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimiento_inventario`
--

LOCK TABLES `movimiento_inventario` WRITE;
/*!40000 ALTER TABLE `movimiento_inventario` DISABLE KEYS */;
/*!40000 ALTER TABLE `movimiento_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pago`
--

DROP TABLE IF EXISTS `pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pago` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `fecha_pago` datetime DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  `impuesto` decimal(10,2) DEFAULT NULL,
  `propina` decimal(10,2) DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `id_cita` int DEFAULT NULL,
  `id_metodo_pago` int DEFAULT NULL,
  `id_promocion` int DEFAULT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `id_cita` (`id_cita`),
  KEY `id_metodo_pago` (`id_metodo_pago`),
  KEY `id_promocion` (`id_promocion`),
  CONSTRAINT `pago_ibfk_1` FOREIGN KEY (`id_cita`) REFERENCES `cita` (`id_cita`),
  CONSTRAINT `pago_ibfk_2` FOREIGN KEY (`id_metodo_pago`) REFERENCES `metodo_pago` (`id_metodo_pago`),
  CONSTRAINT `pago_ibfk_3` FOREIGN KEY (`id_promocion`) REFERENCES `promocion` (`id_promocion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pago`
--

LOCK TABLES `pago` WRITE;
/*!40000 ALTER TABLE `pago` DISABLE KEYS */;
/*!40000 ALTER TABLE `pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos` (
  `id_permisos` int NOT NULL AUTO_INCREMENT,
  `nombre_permisos` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_permisos`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `persona`
--

DROP TABLE IF EXISTS `persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona` (
  `id_persona` int NOT NULL AUTO_INCREMENT,
  `nombre_persona` varchar(50) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(150) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_persona`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona`
--

LOCK TABLES `persona` WRITE;
/*!40000 ALTER TABLE `persona` DISABLE KEYS */;
/*!40000 ALTER TABLE `persona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `codigo_producto` varchar(50) NOT NULL,
  `nombre` varchar(150) DEFAULT NULL,
  `stock_actual` int DEFAULT NULL,
  `precio_compra` decimal(10,2) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  `id_marca` int DEFAULT NULL,
  `id_unidad_medida` int DEFAULT NULL,
  PRIMARY KEY (`codigo_producto`),
  KEY `id_marca` (`id_marca`),
  KEY `id_unidad_medida` (`id_unidad_medida`),
  CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`id_marca`) REFERENCES `marca` (`id_marca`),
  CONSTRAINT `producto_ibfk_2` FOREIGN KEY (`id_unidad_medida`) REFERENCES `unidad_medida` (`id_unidad_medida`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promocion`
--

DROP TABLE IF EXISTS `promocion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promocion` (
  `id_promocion` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) DEFAULT NULL,
  `tipo_promocion` varchar(100) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `valor_descuento` decimal(10,2) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  PRIMARY KEY (`id_promocion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promocion`
--

LOCK TABLES `promocion` WRITE;
/*!40000 ALTER TABLE `promocion` DISABLE KEYS */;
/*!40000 ALTER TABLE `promocion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `id_proveedor` int NOT NULL AUTO_INCREMENT,
  `id_persona` int DEFAULT NULL,
  `rfc` varchar(13) DEFAULT NULL,
  `id_tipo_proveedor` int DEFAULT NULL,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  PRIMARY KEY (`id_proveedor`),
  KEY `id_persona` (`id_persona`),
  KEY `rfc` (`rfc`),
  KEY `id_tipo_proveedor` (`id_tipo_proveedor`),
  CONSTRAINT `proveedor_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  CONSTRAINT `proveedor_ibfk_2` FOREIGN KEY (`rfc`) REFERENCES `empresa` (`rfc`),
  CONSTRAINT `proveedor_ibfk_3` FOREIGN KEY (`id_tipo_proveedor`) REFERENCES `tipo_proveedor` (`id_tipo_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `puesto`
--

DROP TABLE IF EXISTS `puesto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `puesto` (
  `id_puesto` int NOT NULL AUTO_INCREMENT,
  `nombre_puesto` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_puesto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `puesto`
--

LOCK TABLES `puesto` WRITE;
/*!40000 ALTER TABLE `puesto` DISABLE KEYS */;
/*!40000 ALTER TABLE `puesto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(100) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'Administrador','Acceso total a todos los módulos del sistema.'),(2,'Empleado','Gestión de citas y atención al cliente.'),(3,'Cliente','Visualización de catálogo y citas personales.');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol_permiso`
--

DROP TABLE IF EXISTS `rol_permiso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol_permiso` (
  `id_rol_permiso` int NOT NULL AUTO_INCREMENT,
  `id_rol` int DEFAULT NULL,
  `id_permiso` int DEFAULT NULL,
  `id_modulo` int DEFAULT NULL,
  PRIMARY KEY (`id_rol_permiso`),
  KEY `id_rol` (`id_rol`),
  KEY `id_permiso` (`id_permiso`),
  KEY `id_modulo` (`id_modulo`),
  CONSTRAINT `rol_permiso_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`),
  CONSTRAINT `rol_permiso_ibfk_2` FOREIGN KEY (`id_permiso`) REFERENCES `permisos` (`id_permisos`),
  CONSTRAINT `rol_permiso_ibfk_3` FOREIGN KEY (`id_modulo`) REFERENCES `modulo` (`id_modulo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol_permiso`
--

LOCK TABLES `rol_permiso` WRITE;
/*!40000 ALTER TABLE `rol_permiso` DISABLE KEYS */;
/*!40000 ALTER TABLE `rol_permiso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicio`
--

DROP TABLE IF EXISTS `servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicio` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre_servicio` varchar(150) DEFAULT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `duracion_minutos` int DEFAULT NULL,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  `id_categoria` int DEFAULT NULL,
  PRIMARY KEY (`id_servicio`),
  KEY `id_categoria` (`id_categoria`),
  CONSTRAINT `servicio_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicio`
--

LOCK TABLES `servicio` WRITE;
/*!40000 ALTER TABLE `servicio` DISABLE KEYS */;
/*!40000 ALTER TABLE `servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sesion`
--

DROP TABLE IF EXISTS `sesion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesion` (
  `id_sesion` int NOT NULL AUTO_INCREMENT,
  `token_sesion` varchar(255) DEFAULT NULL,
  `fecha_inicio` datetime DEFAULT NULL,
  `fecha_expiracion` datetime DEFAULT NULL,
  `fecha_cierre` datetime DEFAULT NULL,
  `direccion_ip` varchar(45) DEFAULT NULL,
  `dispositivo` varchar(150) DEFAULT NULL,
  `estado` enum('ACTIVA','CERRADA','EXPIRADA') DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  PRIMARY KEY (`id_sesion`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `sesion_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sesion`
--

LOCK TABLES `sesion` WRITE;
/*!40000 ALTER TABLE `sesion` DISABLE KEYS */;
/*!40000 ALTER TABLE `sesion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_proveedor`
--

DROP TABLE IF EXISTS `tipo_proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_proveedor` (
  `id_tipo_proveedor` int NOT NULL AUTO_INCREMENT,
  `tipo_proveedor` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_tipo_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_proveedor`
--

LOCK TABLES `tipo_proveedor` WRITE;
/*!40000 ALTER TABLE `tipo_proveedor` DISABLE KEYS */;
/*!40000 ALTER TABLE `tipo_proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidad_medida`
--

DROP TABLE IF EXISTS `unidad_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidad_medida` (
  `id_unidad_medida` int NOT NULL AUTO_INCREMENT,
  `nombre_unidad` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_unidad_medida`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidad_medida`
--

LOCK TABLES `unidad_medida` WRITE;
/*!40000 ALTER TABLE `unidad_medida` DISABLE KEYS */;
/*!40000 ALTER TABLE `unidad_medida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre_usuario` varchar(100) DEFAULT NULL,
  `contrasenia` varchar(255) DEFAULT NULL,
  `estatus` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
  `ultimo_acceso` datetime DEFAULT NULL,
  `intentos_fallidos` int DEFAULT '0',
  `bloqueado` tinyint(1) DEFAULT '0',
  `id_persona` int DEFAULT NULL,
  `id_rol` int DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  KEY `id_persona` (`id_persona`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  CONSTRAINT `usuario_ibfk_2` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-01 21:03:25
