-- Insert into a la base de datos 
-- Rol
INSERT INTO rol(nombre_rol, descripcion) VALUES 
('Administrador','Acceso total a todos los modulos del sistema.'),
('Empleado','Gestion de citas y atencion al cliente.'),
('Cliente','Visualizacion de catalogos y citas personales,'),
('Proveedor','Vista de falta de inventario.');

-- Empresa
INSERT INTO empresa (rfc, nombre_empresa, direccion, contacto) VALUES 
('VALNBU123451', 'Valentino Beauty', 'Av. Industrial 500, León, Gto.', 'contacto@beautysupply.com'),
('ORGANA123452', 'Organic Nails', 'Calle Rosa 123, Zapopan, Jal.', 'ventas@cosmeticosglam.com'),
('MIASEC123453', 'Mia Secret', 'Blvd. Norte 789, Querétaro, Qro.', 'info@distribuidorabella.com'),
('FANTNA123454', 'Fantasy Nails', 'Privada San José 45, Aguascalientes, Ags.', 'lab@beauty.com'),
('WAPZMA123455', 'Wapizima', 'Av. Reforma 321, CDMX', 'ventas@maquillajepro.com'),
('STUDAL123456', 'Studio Nails', 'Calle Industria 78, Monterrey, NL', 'productos@bella.com'),
('MCIBEL123457', 'Maria Cibeles', 'Blvd. Los Angeles 222, Puebla, Pue.', 'supply@cosmetics.com'),
('MCNAIL123458', 'MC nails', 'Blvd. aeropuesto 225, Puebla, Pue.', 'MCNails@cosmetics.com');

INSERT INTO marca (nombre_marca, rfc) VALUES
('Valentino Beauty', 'VALNBU123451'),
('Organic Nails', 'ORGANA123452'),
('Mia Secret', 'MIASEC123453'),
('Fantasy Nails', 'FANTNA123454'),
('Wapizima', 'WAPZMA123455'),
('Studio Nails', 'STUDAL123456'),
('Maria Cibeles', 'MCIBEL123457'),
('MC Nails', 'MCNAIL123458');

-- Puesto
INSERT INTO puesto (nombre_puesto) VALUES 
('Administrador'),
('Manicurista'),
('Pedicurista')
ON DUPLICATE KEY UPDATE nombre_puesto = VALUES(nombre_puesto);

-- servicios sin foto 
INSERT INTO servicio (nombre_servicio, precio, foto, duracion_minutos, estatus, id_categoria) VALUES
('Uñas acrilicas', 500.00, 'img/servicios/Uñas_acrilicas.jpeg', 120, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Uñas acrilicas' LIMIT 1)),
('Pedicure Spa curativo', 180.00, 'img/servicios/Pedicure_Spa_curativo.jpg', 40, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Pedicure' LIMIT 1)),
('Shellac', 600.00, 'img/servicios/Shellac.jpg', 120, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Uña natural' LIMIT 1)),
('Manicura Básica', 350.00, 'img/servicios/Manicura_básica.jpeg', 80, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Manicure' LIMIT 1)),
('Pedicura Básica', 200.00, 'img/servicios/Pedicura_básica.jpg', 40, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Pedicure' LIMIT 1)),
('Pedicura con estencion de uñas acrilicas', 400.00, 'img/servicios/Pedicura_uñas acrilicas.jpg', 180, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Pedicure y uñas' LIMIT 1)),
('Uñas acrilicas XL', 350.00, 'img/servicios/Uñas_XL.jpeg', 180, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Uñas acrilicas' LIMIT 1));

-- metodos de pago
INSERT INTO metodo_pago (nombre_metodo) VALUES 
('Efectivo'),
('Tarjeta de Débito'),
('Tarjeta de Crédito');

-- Crear HORARIOS
INSERT IGNORE INTO horario (dia, hora_inicio, hora_fin) VALUES
('LUNES', '09:00:00', '20:00:00'),
('MARTES', '09:00:00', '20:00:00'),
('MIERCOLES', '09:00:00', '20:00:00'),
('JUEVES', '09:00:00', '20:00:00'),
('VIERNES', '09:00:00', '20:00:00'),
('SABADO', '09:00:00', '18:00:00');

-- 8. Asignar horario al empleado
INSERT IGNORE INTO empleado_horario (id_empleado, id_horario)
SELECT e.id_empleado, h.id_horario
FROM empleado e, horario h
WHERE e.id_usuario = (SELECT id_usuario FROM usuario WHERE nombre_usuario = 'empleado')
AND h.dia IN ('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO');

INSERT INTO tipo_proveedor (tipo_proveedor) VALUES 
('Valentino Beauty'),
('Organic Nails'),
('Mia Secret'),
('Fantasy Nails'),
('MC Nails'),
('Wapizima'),
('Studio Nails '),
('Maria Cibeles');

INSERT IGNORE INTO horario (dia, hora_inicio, hora_fin) VALUES
('LUNES', '09:00:00', '20:00:00'),
('MARTES', '09:00:00', '20:00:00'),
('MIERCOLES', '09:00:00', '20:00:00'),
('JUEVES', '09:00:00', '20:00:00'),
('VIERNES', '09:00:00', '20:00:00'),
('SABADO', '10:00:00', '15:00:00');

INSERT INTO promocion (nombre, tipo_promocion, descripcion, valor_descuento, foto, estatus) VALUES 
('Manos de Reina', 'Uñas acrilicas', 'Transforma tu estilo con un set de uñas acrílicas diseñado para destacar.', 12.00, 'promo1.jpg', 'ACTIVO'),
('Máximo Estilo XL', 'Uñas acrilicas XL', 'Luce un set de uñas acrílicas XL con el largo y diseño que siempre quisiste.', 30.00, 'promo2.jpg', 'ACTIVO'),
('Cumpleaños Glam', 'Manicura Básica', '¡Celebra tu día con nosotros! Disfruta de una manicura básica profesional para lucir unas manos impecables en tu mes especial.', 20.00, 'promo3.jpg', 'ACTIVO');

INSERT INTO categoria (nombre_categoria) VALUES 
('Uñas acrilicas'),
('Pedicure'),
('Uña natural'),
('Manicure'),
('Pedicure y uñas');

INSERT INTO persona (nombre_persona, apellidos, telefono, correo, direccion) VALUES 
('Jimena', 'Oropeza Cruces', '4771234567', 'jimena@beautyglam.com', 'Calle Principal 123, León'),
('Emiliano', 'Rodríguez Lopez', '4777654321', 'roberto.profe@utl.edu.mx', 'Av. Universidad 456, León'),
('Ana', 'García Perez', '4779876543', 'ana.cliente@gmail.com', 'Col. Centro 789, León');

INSERT INTO usuario (nombre_usuario, contrasenia, id_rol, estatus) VALUES 
('admin', 'admin123', 1, 'ACTIVO'),
('empleado', 'emp123', 2, 'ACTIVO'),
('cliente1', 'cli123', 3, 'ACTIVO');

INSERT INTO unidad_medida (nombre_unidad) VALUES 
('Mililitros'),
('Onzas'),
('Gramo'),
('Pieza'),
('Paquete');

-- Cliente 1
CALL sp_crear_cliente(
'Ana', 'García López', 
'4771234560', 
'ana.garcia@gmail.com', 
'Col. Centro, León', 
'ana_garcia', 
'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1995-03-15', 'Femenino');

-- Cliente 2
CALL sp_crear_cliente(
'Beatriz', 'Rodríguez', 
'4772345671', 
'betty_rod@yahoo.com', 
'Valle del Campestre, León', 
'betty_rod', 'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea',
'1990-10-20', 'Femenino');

-- Cliente 3
CALL sp_crear_cliente(
'Carlos', 'Martínez', 
'4773456782', 
'carlos.mtz@outlook.com', 
'Jardines de Jerez, León', 
'carlos_mtz', 'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1988-05-05', 'Masculino');

-- Cliente 4
CALL sp_crear_cliente(
'Diana', 
'Sánchez P.', 
'4774567893', 
'diana_sp@gmail.com', 
'El Coecillo, León', 
'diana_salon', 
'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'2002-12-12', 'Femenino');

-- Cliente 5
CALL sp_crear_cliente(
'Eduardo', 'Torres', 
'4775678904', 
'lalo_torres@prodigy.net', 
'Lomas de León', 'lalo_t', 
'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1998-07-25', 'Masculino');


-- Empleado 1: Estilista Senior
CALL sp_crear_empleado(
'Laura', 
'Méndez', 
'4776789015', 
'laura.m@salon.com', 
'Col. Moderna', 1, 
'2026-01-10', 
'laura_hair', 'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', '1992-04-10', 'Femenino');

-- Empleado 2: Especialista en Uñas
CALL sp_crear_empleado(
'Sofía', 'Castro', 
'4777890126', 
'sofia.c@salon.com', 
'Col. Andrade', 2, 
'2026-02-15', 
'sofia_nails', 
'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1995-08-22', 'Femenino');

-- Empleado 3: Recepcionista
CALL sp_crear_empleado(
'Jorge', 
'Luna', 
'4778901237', 
'jorge.l@salon.com', 
'San Juan de Dios', 3, 
'2026-03-01', 
'jorge_admin', 
'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1985-11-30', 'Masculino');

-- Empleado 4: Estilista Jr.
CALL sp_crear_empleado(
'Mariana', 
'Ruiz', 
'4779012348', 
'mariana.r@salon.com', 
'Col. Roma', 1, 
'2026-03-20', 
'mariana_hair', 
'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'2000-01-05', 'Femenino');

-- Empleado 5: Colorista
CALL sp_crear_empleado(
'Ricardo', 
'Sosa', 
'4770123459', 
'ricardo.s@salon.com', 
'León Moderno', 1, 
CURDATE(), 
'ricardo_pro', 
'scrypt:32768:8:1$eArbDZFRs0xF6JWo$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1990-06-18', 'Masculino');


-- Proveedor 1
CALL sp_crear_proveedor(
'Héctor', 
'Villalobos', 
'4771002030', 
'h.villalobos@wella.mx', 
'Blvd. Adolfo López Mateos 120', 
'WAPZMA123455', 1, 
'hector_tinte', 
'$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1985-05-20', 'Masculino');

-- Proveedor 2
CALL sp_crear_proveedor(
'Claudia', 
'Jiménez', 
'4773004050', 
'claudia.j@protools.com', 
'Calle Pino Suárez 405', 
'FANTNA123454', 2, 
'clau_tools', 
'$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1992-11-12', 'Femenino');

-- Proveedor 3
CALL sp_crear_proveedor(
'Samuel', 
'Ortiz', 
'3315006070', 
'sam.muebles@beautyfurniture.com', 
'Zona Industrial Gdl', 
'MIASEC123453', 3, 
'samuel_muebles', '
$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1978-02-28', 'Masculino');

-- Proveedor 4
CALL sp_crear_proveedor(
'Ximena', 
'Rojas', 
'5540005060', 
'xrojas@higienepro.com', 
'Col. Roma Norte, CDMX', 
'ORGANA123452', 4, 
'ximena_clean', 
'$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'2000-08-15', 'Femenino');

-- Proveedor 5
CALL sp_crear_proveedor(
'Alex', 
'Vargas', 
'4776007080', 
'alex.v@consultoria.com', 
'Col. León Moderno', 
'VALNBU123451', 5, 
'alex_tech', 
'$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
'1995-12-31', 'Otro');