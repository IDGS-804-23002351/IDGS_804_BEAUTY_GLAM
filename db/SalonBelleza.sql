DROP DATABASE IF EXISTS salon_belleza;
CREATE DATABASE salon_belleza;
USE salon_belleza;

CREATE TABLE persona (
 id_persona INT AUTO_INCREMENT PRIMARY KEY,
 nombre_persona VARCHAR(50),
 apellidos VARCHAR(100),
 telefono VARCHAR(20),
 correo VARCHAR(150),
 direccion VARCHAR(255)
);

CREATE TABLE empresa (
rfc VARCHAR(13) PRIMARY KEY,
nombre_empresa VARCHAR(150),
direccion VARCHAR(255),
contacto VARCHAR(150)
);

-- Es un conjunto de permisos en el software
CREATE TABLE modulo (
    id_modulo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_modulo VARCHAR(100) NOT NULL
);

CREATE TABLE rol(
id_rol INT AUTO_INCREMENT PRIMARY KEY,
nombre_rol VARCHAR(100),
descripcion VARCHAR(255)
);

CREATE TABLE permisos(
id_permisos INT AUTO_INCREMENT PRIMARY KEY,
nombre_permisos VARCHAR(100)
);

CREATE TABLE rol_permiso (
    id_rol_permiso INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT,
    id_permiso INT,
    id_modulo INT,
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol),
    FOREIGN KEY (id_permiso) REFERENCES permisos(id_permisos),
    FOREIGN KEY (id_modulo) REFERENCES modulo(id_modulo)
);

CREATE TABLE usuario (
id_usuario INT AUTO_INCREMENT PRIMARY KEY,
nombre_usuario VARCHAR(100) UNIQUE,
contrasenia VARCHAR(255),
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
ultimo_acceso DATETIME,
intentos_fallidos INT DEFAULT 0,
bloqueado TINYINT(1) DEFAULT 0,
id_persona INT,
id_rol INT,
FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
);

CREATE TABLE cliente (
id_cliente INT AUTO_INCREMENT PRIMARY KEY,
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
id_persona INT,
id_usuario INT,
FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- descripción laboral, Sirve para nómina, horarios y funciones físicas.
CREATE TABLE puesto (
id_puesto INT AUTO_INCREMENT PRIMARY KEY,
nombre_puesto VARCHAR(100)
);

CREATE TABLE empleado (
id_empleado INT AUTO_INCREMENT PRIMARY KEY,
fecha_contratacion DATE,
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
id_persona INT,
id_puesto INT,
id_usuario INT,
FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
FOREIGN KEY (id_puesto) REFERENCES puesto(id_puesto),
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE categoria (
id_categoria INT AUTO_INCREMENT PRIMARY KEY,
nombre_categoria VARCHAR(100)
);

CREATE TABLE servicio (
id_servicio INT AUTO_INCREMENT PRIMARY KEY,
nombre_servicio VARCHAR(150),
precio DECIMAL(10,2),
duracion_minutos INT,
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
id_categoria INT,
FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
);

CREATE TABLE cita (
id_cita INT AUTO_INCREMENT PRIMARY KEY,
fecha_hora DATETIME,
estatus ENUM('PENDIENTE','CONFIRMADA','CANCELADA','FINALIZADA') DEFAULT 'PENDIENTE',
id_cliente INT,
id_empleado INT,
FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
);

CREATE TABLE detalle_cita (
id_detalle_cita INT AUTO_INCREMENT PRIMARY KEY,
id_cita INT,
id_servicio INT,
subtotal DECIMAL(10,2),
FOREIGN KEY (id_cita) REFERENCES cita(id_cita),
FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio)
);

CREATE TABLE metodo_pago (
id_metodo_pago INT AUTO_INCREMENT PRIMARY KEY,
nombre_metodo VARCHAR(100)
);

CREATE TABLE promocion (
id_promocion INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR (255),
tipo_promocion VARCHAR(100),
descripcion VARCHAR(255),
valor_descuento DECIMAL(10,2),
foto VARCHAR (255),
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO'
);

CREATE TABLE pago (
id_pago INT AUTO_INCREMENT PRIMARY KEY,
fecha_pago DATETIME,
subtotal DECIMAL(10,2),
impuesto DECIMAL(10,2),
propina DECIMAL(10,2),
total DECIMAL(10,2),
id_cita INT,
id_metodo_pago INT,
id_promocion INT,
FOREIGN KEY (id_cita) REFERENCES cita(id_cita),
FOREIGN KEY (id_metodo_pago) REFERENCES metodo_pago(id_metodo_pago),
FOREIGN KEY (id_promocion) REFERENCES promocion(id_promocion)
);

CREATE TABLE horario (
id_horario INT AUTO_INCREMENT PRIMARY KEY,
dia ENUM('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO'),
hora_inicio TIME,
hora_fin TIME
);

CREATE TABLE empleado_horario (
id_empleado INT,
id_horario INT,
PRIMARY KEY (id_empleado, id_horario),
FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado),
FOREIGN KEY (id_horario) REFERENCES horario(id_horario)
);

CREATE TABLE marca (
id_marca INT AUTO_INCREMENT PRIMARY KEY,
nombre_marca VARCHAR(100),
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
rfc VARCHAR(13),
FOREIGN KEY (rfc) REFERENCES empresa(rfc)
);

CREATE TABLE unidad_medida (
id_unidad_medida INT AUTO_INCREMENT PRIMARY KEY,
nombre_unidad VARCHAR(50)
);

CREATE TABLE producto (
codigo_producto VARCHAR(50) PRIMARY KEY,
nombre VARCHAR(150),
stock_actual INT,
precio_compra DECIMAL(10,2),
precio_unitario DECIMAL(10,2),
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
id_marca INT,
id_unidad_medida INT,
FOREIGN KEY (id_marca) REFERENCES marca(id_marca),
FOREIGN KEY (id_unidad_medida) REFERENCES unidad_medida(id_unidad_medida)
);

CREATE TABLE insumo_servicio (
id_insumo_servicio INT AUTO_INCREMENT PRIMARY KEY,
id_servicio INT,
codigo_producto VARCHAR(50),
cantidad_utilizada DECIMAL(10,2),
FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio),
FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

CREATE TABLE tipo_proveedor (
id_tipo_proveedor INT AUTO_INCREMENT PRIMARY KEY,
tipo_proveedor VARCHAR(100)
);

CREATE TABLE proveedor (
id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
id_persona INT,
rfc VARCHAR(13),
id_tipo_proveedor INT,
estatus ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
FOREIGN KEY (rfc) REFERENCES empresa(rfc),
FOREIGN KEY (id_tipo_proveedor) REFERENCES tipo_proveedor(id_tipo_proveedor)
);

CREATE TABLE sesion (
id_sesion INT AUTO_INCREMENT PRIMARY KEY,
token_sesion VARCHAR(255),
fecha_inicio DATETIME,
fecha_expiracion DATETIME,
fecha_cierre DATETIME,
direccion_ip VARCHAR(45),
dispositivo VARCHAR(150),
estado ENUM('ACTIVA','CERRADA','EXPIRADA'),
id_usuario INT,
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- se agrego de la base de datos de Oscar Miguel para tomar en cuenta el inventario el conteo de la materia prima 
CREATE TABLE inventario_producto (
codigo_producto VARCHAR(50) PRIMARY KEY,
stock_minimo INT DEFAULT 0,
stock_maximo INT DEFAULT 0,
ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

CREATE TABLE movimiento_inventario (
id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
codigo_producto VARCHAR(50),
tipo ENUM('ENTRADA','SALIDA','AJUSTE'),
cantidad INT,
motivo VARCHAR(150),
fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

CREATE TABLE compra_proveedor (
id_compra_proveedor INT AUTO_INCREMENT PRIMARY KEY,
fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
total DECIMAL(10,2),
id_proveedor INT,
FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor)
);

CREATE TABLE detalle_compra (
id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
id_compra_proveedor INT,
codigo_producto VARCHAR(50),
cantidad INT,
precio_unitario DECIMAL(10,2),
subtotal DECIMAL(10,2),
FOREIGN KEY (id_compra_proveedor) REFERENCES compra_proveedor(id_compra_proveedor),
FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

-- Descuento por servicio en detalle de cita
ALTER TABLE detalle_cita
ADD descuento DECIMAL(10,2) DEFAULT 0;

CREATE TABLE historial_estatus (
id INT AUTO_INCREMENT PRIMARY KEY,
tabla_afectada VARCHAR(100) NOT NULL,
id_registro INT NOT NULL,
estatus_anterior VARCHAR(50),
estatus_nuevo VARCHAR(50) NOT NULL,
fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detalle_pago (
id_detalle_pago INT AUTO_INCREMENT PRIMARY KEY,
id_pago INT,
id_metodo_pago INT,
monto DECIMAL(10,2),
FOREIGN KEY (id_pago) REFERENCES pago(id_pago),
FOREIGN KEY (id_metodo_pago) REFERENCES metodo_pago(id_metodo_pago)
);

CREATE TABLE bitacora(
id_bitacora INT AUTO_INCREMENT PRIMARY KEY,
accion VARCHAR(100), -- Actualizó stock del producto
fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
tabla_afectada VARCHAR(100),
id_registro_afectado INT,
id_usuario INT,   -- Quien lo hizo
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);