DROP DATABASE IF EXISTS salon_belleza;
CREATE DATABASE IF NOT EXISTS salon_belleza;
USE salon_belleza;

-- 1. TABLA PERSONA (Base para Usuarios, Clientes, Empleados)
CREATE TABLE persona (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    nombre_persona VARCHAR(50),
    apellidos VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(150),
    direccion VARCHAR(255),
    fecha_nacimiento DATE,
    genero ENUM('Femenino', 'Masculino', 'Otro', 'Sin especificar') DEFAULT 'Sin especificar',
    ultima_actualizacion DATETIME
);

-- 2. TABLA EMPRESA
CREATE TABLE empresa (
    rfc VARCHAR(13) PRIMARY KEY,
    nombre_empresa VARCHAR(150),
    direccion VARCHAR(255),
    contacto VARCHAR(150)
);

-- 3. TABLA ROL
CREATE TABLE rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(100),
    descripcion VARCHAR(255),
    estatus VARCHAR(20) DEFAULT 'ACTIVO'
);

-- 4. TABLA MODULO
CREATE TABLE modulo (
    id_modulo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_modulo VARCHAR(100) NOT NULL
);

-- 5. TABLA PERMISOS
CREATE TABLE permisos (
    id_permisos INT AUTO_INCREMENT PRIMARY KEY,
    nombre_permisos VARCHAR(100)
);

-- 6. TABLA ROL_PERMISO (Relación muchos a muchos)
CREATE TABLE rol_permiso (
    id_rol_permiso INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT,
    id_permiso INT,
    id_modulo INT,
    CONSTRAINT fk_rol_permiso_rol FOREIGN KEY (id_rol) REFERENCES rol(id_rol),
    CONSTRAINT fk_rol_permiso_permiso FOREIGN KEY (id_permiso) REFERENCES permisos(id_permisos),
    CONSTRAINT fk_rol_permiso_modulo FOREIGN KEY (id_modulo) REFERENCES modulo(id_modulo)
);

-- 7. TABLA USUARIO
CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(100) UNIQUE,
    contrasenia VARCHAR(255),
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    ultimo_acceso DATETIME,
    intentos_fallidos INT DEFAULT 0,
    bloqueado BOOLEAN DEFAULT FALSE,
    id_persona INT,
    id_rol INT,
    CONSTRAINT fk_usuario_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
    CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
);

-- 8. TABLA SESION
CREATE TABLE sesion (
    id_sesion INT AUTO_INCREMENT PRIMARY KEY,
    token_sesion VARCHAR(255),
    fecha_inicio DATETIME,
    fecha_expiracion DATETIME,
    fecha_cierre DATETIME,
    direccion_ip VARCHAR(45),
    dispositivo VARCHAR(150),
    estado ENUM('ACTIVA', 'CERRADA', 'EXPIRADA'),
    id_usuario INT,
    id_rol INT,
    CONSTRAINT fk_sesion_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_sesion_rol FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
);

-- 9. TABLA PUESTO
CREATE TABLE puesto (
    id_puesto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_puesto VARCHAR(100)
);

-- 10. TABLA EMPLEADO
CREATE TABLE empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    fecha_contratacion DATE,
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    id_persona INT,
    id_puesto INT,
    id_usuario INT,
    CONSTRAINT fk_empleado_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
    CONSTRAINT fk_empleado_puesto FOREIGN KEY (id_puesto) REFERENCES puesto(id_puesto),
    CONSTRAINT fk_empleado_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- 11. TABLA HORARIO
CREATE TABLE horario (
    id_horario INT AUTO_INCREMENT PRIMARY KEY,
    dia ENUM('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO'),
    hora_inicio TIME,
    hora_fin TIME
);

-- 12. TABLA INTERMEDIA EMPLEADO_HORARIO
CREATE TABLE empleado_horario (
    id_empleado INT,
    id_horario INT,
    PRIMARY KEY (id_empleado, id_horario),
    CONSTRAINT fk_eh_empleado FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado),
    CONSTRAINT fk_eh_horario FOREIGN KEY (id_horario) REFERENCES horario(id_horario)
);

-- 13. TABLA CLIENTE
CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    id_persona INT,
    id_usuario INT,
    CONSTRAINT fk_cliente_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
    CONSTRAINT fk_cliente_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- 14. TABLA CATEGORIA
CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100)
);

-- 15. TABLA SERVICIO
CREATE TABLE servicio (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre_servicio VARCHAR(150),
    precio DECIMAL(10, 2),
    foto VARCHAR(255),
    duracion_minutos INT,
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    id_categoria INT,
    CONSTRAINT fk_servicio_categoria FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
);

-- 16. TABLA CITA
CREATE TABLE cita (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME,
    estatus ENUM('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'FINALIZADA') DEFAULT 'PENDIENTE',
    id_cliente INT,
    id_empleado INT,
    CONSTRAINT fk_cita_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    CONSTRAINT fk_cita_empleado FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
);

-- 17. TABLA DETALLE_CITA
CREATE TABLE detalle_cita (
    id_detalle_cita INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT,
    id_servicio INT,
    subtotal DECIMAL(10, 2),
    descuento DECIMAL(10, 2) DEFAULT 0.00,
    CONSTRAINT fk_detalle_cita_cita FOREIGN KEY (id_cita) REFERENCES cita(id_cita),
    CONSTRAINT fk_detalle_cita_servicio FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio)
);

-- 18. TABLA METODO_PAGO
CREATE TABLE metodo_pago (
    id_metodo_pago INT AUTO_INCREMENT PRIMARY KEY,
    nombre_metodo VARCHAR(100)
);

-- 19. TABLA PROMOCION
CREATE TABLE promocion (
    id_promocion INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    tipo_promocion VARCHAR(100),
    descripcion VARCHAR(255),
    valor_descuento DECIMAL(10, 2),
    foto VARCHAR(255),
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO'
);

-- 20. TABLA PAGO
CREATE TABLE pago (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    fecha_pago DATETIME,
    subtotal DECIMAL(10, 2),
    impuesto DECIMAL(10, 2),
    propina DECIMAL(10, 2),
    total DECIMAL(10, 2),
    id_cita INT,
    id_metodo_pago INT,
    id_promocion INT,
    CONSTRAINT fk_pago_cita FOREIGN KEY (id_cita) REFERENCES cita(id_cita),
    CONSTRAINT fk_pago_metodo FOREIGN KEY (id_metodo_pago) REFERENCES metodo_pago(id_metodo_pago),
    CONSTRAINT fk_pago_promocion FOREIGN KEY (id_promocion) REFERENCES promocion(id_promocion)
);

-- 21. TABLA DETALLE_PAGO
CREATE TABLE detalle_pago (
    id_detalle_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_pago INT,
    id_metodo_pago INT,
    monto DECIMAL(10, 2),
    CONSTRAINT fk_detalle_pago_pago FOREIGN KEY (id_pago) REFERENCES pago(id_pago),
    CONSTRAINT fk_detalle_pago_metodo FOREIGN KEY (id_metodo_pago) REFERENCES metodo_pago(id_metodo_pago)
);

-- 22. TABLA MARCA
CREATE TABLE marca (
    id_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre_marca VARCHAR(100),
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    rfc VARCHAR(13),
    CONSTRAINT fk_marca_empresa FOREIGN KEY (rfc) REFERENCES empresa(rfc)
);

-- 23. TABLA UNIDAD_MEDIDA
CREATE TABLE unidad_medida (
    id_unidad_medida INT AUTO_INCREMENT PRIMARY KEY,
    nombre_unidad VARCHAR(50)
);

-- 24. TABLA PRODUCTO
CREATE TABLE producto (
    codigo_producto VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(150),
    stock_actual INT,
    precio_compra DECIMAL(10, 2),
    precio_unitario DECIMAL(10, 2),
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    id_marca INT,
    id_unidad_medida INT,
    CONSTRAINT fk_producto_marca FOREIGN KEY (id_marca) REFERENCES marca(id_marca),
    CONSTRAINT fk_producto_unidad FOREIGN KEY (id_unidad_medida) REFERENCES unidad_medida(id_unidad_medida)
);

-- 25. TABLA INSUMO_SERVICIO
CREATE TABLE insumo_servicio (
    id_insumo_servicio INT AUTO_INCREMENT PRIMARY KEY,
    id_servicio INT,
    codigo_producto VARCHAR(50),
    cantidad_utilizada DECIMAL(10, 2),
    CONSTRAINT fk_insumo_servicio FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio),
    CONSTRAINT fk_insumo_producto FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

-- 26. TABLA TIPO_PROVEEDOR
CREATE TABLE tipo_proveedor (
    id_tipo_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    tipo_proveedor VARCHAR(100)
);

-- 27. TABLA PROVEEDOR
CREATE TABLE proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    rfc VARCHAR(13),
    id_tipo_proveedor INT,
    estatus ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    CONSTRAINT fk_proveedor_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
    CONSTRAINT fk_proveedor_empresa FOREIGN KEY (rfc) REFERENCES empresa(rfc),
    CONSTRAINT fk_proveedor_tipo FOREIGN KEY (id_tipo_proveedor) REFERENCES tipo_proveedor(id_tipo_proveedor)
);

-- 28. TABLA INVENTARIO_PRODUCTO
CREATE TABLE inventario_producto (
    codigo_producto VARCHAR(50) PRIMARY KEY,
    stock_minimo INT DEFAULT 0,
    stock_maximo INT DEFAULT 0,
    ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_inventario_producto FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

-- 29. TABLA MOVIMIENTO_INVENTARIO
CREATE TABLE movimiento_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    codigo_producto VARCHAR(50),
    tipo ENUM('ENTRADA', 'SALIDA', 'AJUSTE'),
    cantidad INT,
    motivo VARCHAR(150),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movimiento_producto FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

-- 30. TABLA COMPRA_PROVEEDOR
CREATE TABLE compra_proveedor (
    id_compra_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2),
    id_proveedor INT,
    CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor)
);

-- 31. TABLA DETALLE_COMPRA
CREATE TABLE detalle_compra (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_compra_proveedor INT,
    codigo_producto VARCHAR(50),
    cantidad INT,
    precio_unitario DECIMAL(10, 2),
    subtotal DECIMAL(10, 2),
    CONSTRAINT fk_detalle_compra_compra FOREIGN KEY (id_compra_proveedor) REFERENCES compra_proveedor(id_compra_proveedor),
    CONSTRAINT fk_detalle_compra_producto FOREIGN KEY (codigo_producto) REFERENCES producto(codigo_producto)
);

-- 32. TABLA HISTORIAL_ESTATUS
CREATE TABLE historial_estatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tabla_afectada VARCHAR(100) NOT NULL,
    id_registro INT NOT NULL,
    estatus_anterior VARCHAR(50),
    estatus_nuevo VARCHAR(50) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 33. TABLA BITACORA (SQL)
CREATE TABLE bitacora (
    id_bitacora INT AUTO_INCREMENT PRIMARY KEY,
    accion VARCHAR(100),
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    tabla_afectada VARCHAR(100),
    id_registro_afectado INT,
    id_usuario INT,
    CONSTRAINT fk_bitacora_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

