USE salon_belleza;

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
('WAPZMA123455', 'Wapizima', 'Av. Reforma 321, CDMX', 'ventas@beautypro.com'),
('STUDAL123456', 'Studio Nails', 'Calle Industria 78, Monterrey, NL', 'productos@bella.com'),
('MCIBEL123457', 'Maria Cibeles', 'Blvd. Los Angeles 222, Puebla, Pue.', 'supply@cosmetics.com'),
('MCNAIL123458', 'MC nails', 'Blvd. aeropuesto 225, Puebla, Pue.', 'MCNails@cosmetics.com'),
('SCOTTSOP1234', 'Scott-Shop', 'Av. Industrial 500, León, Gto.', 'contacto@beautysupply.com'),
('PROTEC761234', 'Protec', 'Av. Industrial 500, León, Gto.', 'contacto@beautysupply.com');

-- Marca
INSERT INTO marca (nombre_marca, rfc) VALUES
('Valentino Beauty', 'VALNBU123451'),
('Organic Nails', 'ORGANA123452'),
('Mia Secret', 'MIASEC123453'),
('Fantasy Nails', 'FANTNA123454'),
('Wapizima', 'WAPZMA123455'),
('Studio Nails', 'STUDAL123456'),
('Maria Cibeles', 'MCIBEL123457'),
('MC Nails', 'MCNAIL123458'),
('Protec','PROTEC761234'),
('Scott-Shop','SCOTTSOP1234');

-- Puesto
INSERT INTO puesto (nombre_puesto) VALUES 
('Administrador'),
('Manicurista'),
('Pedicurista')
ON DUPLICATE KEY UPDATE nombre_puesto = VALUES(nombre_puesto);

-- CATEGORIAS (movido antes de servicios)
INSERT INTO categoria (nombre_categoria) VALUES 
('Uñas acrilicas'),
('Pedicure'),
('Uña natural'),
('Manicure'),
('Pedicure y uñas');

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
'samuel_muebles', 
'$beeac0ec6d7669400314866a2c72bbfe8a7465e1f14f395cb0df85f1bd5460a46ea96d7f3ad33043c147f4d18e6fb4c78fb1ea9ec9d717c9e23de6ea315227ea', 
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

INSERT INTO producto (codigo_producto, nombre, foto, stock_actual, precio_compra, precio_unitario, estatus, id_marca, id_unidad_medida) VALUES
('PG443', 'Anti-hongos', 'Anti-Hongos-bliss-MC-Nails.jpg', 149.75, 525.00, 0.00, 'ACTIVO', 8, 1),
('PG1111', 'Limas #80 #100 #120', 'Limas Para Uñas 50 Pzas.jpg', 6.00, 1700.00, 0.00, 'ACTIVO', 5, 4),
('PG1112', 'Limas sponch', 'Spoch Uñas.jpg', 15.00, 400.00, 0.00, 'ACTIVO', 4, 4),
('PG1113', 'Bledo', 'Bledo.png', 3.00, 210.00, 0.00, 'ACTIVO', 5, 4),
('PG1114', 'Empujadores de cuticula', 'EmpujadoresCuticula.jpeg', 11.00, 1440.00, 0.00, 'ACTIVO', 4, 4),
('PG441', 'Cogin', 'Cojin_reposabrazo.jpg', 6.00, 595.00, 0.00, 'ACTIVO', 2, 4),
('PG4410', 'Monomero', 'Monomero-Cibeles-4Oz.webp', 127.00, 2160.00, 0.00, 'ACTIVO', 7, 2),
('PG4415', 'Anticeptico', 'Anticeptico.webp', 959.50, 240.00, 0.00, 'ACTIVO', 8, 1),
('PG4417', 'Finish gel UV', 'Finish gel UV.jpeg', 149.75, 675.00, 0.00, 'ACTIVO', 1, 1),
('PG4418', 'Aceite de cuticula', 'AceitedeCutA_cula15mlMCNails_png_1024x.webp', 149.75, 450.00, 0.00, 'ACTIVO', 8, 1),
('PG4419', 'Lampara UV', 'lampara.jpeg', 4.00, 1052.00, 0.00, 'ACTIVO', 8, 4),
('PG442', 'Primer adherente', 'Primer_adherente.webp', 149.75, 525.00, 0.00, 'ACTIVO', 8, 1),
('PG4421', 'Acetona pura', 'AcetonaPura.webp', 159.75, 350.00, 0.00, 'ACTIVO', 4, 2),
('PG4422', 'Decoracion', 'decoracion.jpg', 14.00, 700.00, 0.00, 'ACTIVO', 3, 5),
('PG4424', 'Removedor de cuticula', 'removedor de cuticula.jpeg', 240.00, 320.00, 0.00, 'ACTIVO', 8, 3),
('PG4425', 'Alicatas', 'alicatas.jpeg', 10.00, 500.00, 0.00, 'ACTIVO', 8, 4),
('PG4426', 'Tijeras', 'TijeraParaCuticulaPremiumFantasyNails_1024x.webp', 4.00, 625.00, 0.00, 'ACTIVO', 4, 4),
('PG4427', 'Exfoliante', 'exfoliantePedicure.jpeg', 700.00, 350.00, 0.00, 'ACTIVO', 1, 3),
('PG4428', 'Mascarilla', 'mascarilla_pedicure.jpeg', 700.00, 400.00, 0.00, 'ACTIVO', 8, 3),
('PG4429', 'Limpia pincel', 'Limpia_pincel.jpeg', 25.00, 300.00, 0.00, 'ACTIVO', 2, 2),
('PG4430', 'Crema humectante', 'Crema humectante.webp', 1500.00, 800.00, 0.00, 'ACTIVO', 8, 3),
('PG4431', 'Alcohol', 'alchool.png', 900.00, 700.00, 0.00, 'ACTIVO', 1, 1),
('PG4432', 'Toallas secado', 'Tollas_rosas.jpg', 20.00, 800.00, 0.00, 'ACTIVO', 4, 4),
('PG4433', 'Algodon', 'TorundaAlgodonProtec.jpg', 800.00, 500.00, 0.00, 'ACTIVO', 10, 3),
('PG4434', 'Removedor de esmalte', 'RemovedorMagic15mlFantasyNails_grande.webp', 150.00, 450.00, 0.00, 'ACTIVO', 4, 1),
('PG4435', 'Palitos de naranjo', 'Palitos de naranjo.jpg', 500.00, 120.00, 0.00, 'ACTIVO', 6, 4),
('PG4436', 'Guantes de nitrilo', 'GuantesNitrilo.jpg', 14.00, 240.00, 0.00, 'ACTIVO', 3, 5),
('PG4437', 'Cubrebocas', 'cubrebocas.webp', 19.00, 120.00, 0.00, 'ACTIVO', 10, 4),
('PG4438', 'Pedicure bowl', 'recipientePedicure.jpeg', 7.00, 2450.00, 0.00, 'ACTIVO', 7, 4),
('PG4439', 'Macure bowl', 'recipienteManicure.jpeg', 5.00, 120.00, 0.00, 'ACTIVO', 4, 5),
('PG444', 'Servi-toallas', 'servi-Toalla-Azul-scott-shop.jpg', 7.90, 56.00, 0.00, 'ACTIVO', 9, 5),
('PG445', 'pincel kolinsky #10', 'Pincel kolinsky #10.jpeg', 4.00, 1850.00, 0.00, 'ACTIVO', 8, 4),
('PG446', 'Pincel kolinsky #8', 'Pincel kolinsky #8.jpeg', 5.00, 1600.00, 0.00, 'ACTIVO', 8, 4),
('PG447', 'Pincel kolinsky #2 3D', 'Pincel kolinsky #2 3D.jpeg', 4.00, 1840.00, 0.00, 'ACTIVO', 1, 4),
('PG448', 'pincel kolinsky 3d #4', 'pincel kolinsky 3d #4.webp', 5.00, 1850.00, 0.00, 'ACTIVO', 8, 4),
('PG449', 'Godete de vidrio', 'Godete.jpg', 7.00, 105.00, 0.00, 'ACTIVO', 8, 4),
('PP221', 'Bombas efervecentes', 'BombasEfervecentes.jpg', 72.00, 450.00, 0.00, 'ACTIVO', 8, 4),
('PP222', 'Sales minerales', 'SalesMinerales.jpg', 1000.00, 850.00, 0.00, 'ACTIVO', 8, 3),
('PP223', 'Removedor de callos', 'REMOVEDORCallos.webp', 240.00, 320.00, 0.00, 'ACTIVO', 8, 3),
('PU111', 'Tip', 'Tips.jpeg', 5.00, 60.00, 0.00, 'ACTIVO', 4, 5),
('PU112', 'Corta tip', 'CortaTip.jpeg', 2.00, 100.00, 0.00, 'ACTIVO', 8, 4),

-- PRODUCTOS DE COLOR NUEVOS
('ESM001', 'acrilico rosa', 'acrilicoRosa.webp', 20.00, 130.00, 0.00, 'ACTIVO', 8, 1),
('ESM002', 'acrilico rojo', 'acrilico_rojo.jpeg', 18.00, 130.00, 0.00, 'ACTIVO', 8, 1),
('ESM003', 'acrilico nude', 'acrilico_nude.webp', 16.00, 130.00, 0.00, 'ACTIVO', 8, 1),
('ESM004', 'acrilico transparente', 'acrilico_trasparente.webp', 16.00, 130.00, 0.00, 'ACTIVO', 8, 1),
('ESM005', 'acrilico blanco', 'acrilicoblanco1.2oz.webp', 16.00, 130.00, 0.00, 'ACTIVO', 8, 1),
('ESM006', 'gelish negro', 'gelish_negro.webp', 25.00, 110.00, 0.00, 'ACTIVO', 5, 1),
('ESM007', 'gelish blanco', 'gelish_blanco.webp', 25.00, 110.00, 0.00, 'ACTIVO', 5, 1);

INSERT INTO movimiento_inventario (id_movimiento, codigo_producto, tipo, cantidad, motivo, fecha) VALUES
(1, 'PG4418', 'ENTRADA', 150, 'Compra de inicio', '2026-04-15 17:43:33'),
(2, 'PG4421', 'ENTRADA', 160, 'Inicio de compra', '2026-04-15 17:46:56'),
-- (3, 'PG4416', 'ENTRADA', 10, 'Movimineto inicial', '2026-04-15 17:49:56'),
(4, 'PG4431', 'ENTRADA', 900, 'Movimineto inicial', '2026-04-15 17:50:56'),
(5, 'PG4433', 'ENTRADA', 7, 'Movimineto inicial', '2026-04-15 17:51:30'),
(6, 'PG4433', 'ENTRADA', 793, 'Movimineto inicial', '2026-04-15 17:52:34'),
(7, 'PG4425', 'ENTRADA', 10, 'Movimineto inicial', '2026-04-15 17:54:00'),
(8, 'PG443', 'ENTRADA', 150, 'Movimineto inicial', '2026-04-15 17:54:41'),
(9, 'PG4415', 'ENTRADA', 960, 'Movimineto inicial', '2026-04-15 17:56:12'),
(10, 'PG1113', 'ENTRADA', 4, 'Movimineto inicial', '2026-04-15 17:57:34'),
(11, 'PP221', 'ENTRADA', 72, 'Movimineto inicial', '2026-04-15 17:58:49'),
(12, 'PG441', 'ENTRADA', 7, 'Movimineto inicial', '2026-04-15 17:59:21'),
(13, 'PU112', 'ENTRADA', 2, 'Movimineto inicial', '2026-04-15 17:59:42'),
(14, 'PG4430', 'ENTRADA', 1500, 'Movimineto inicial', '2026-04-15 18:00:59'),
(15, 'PG4437', 'ENTRADA', 20, 'Movimineto inicial', '2026-04-15 18:01:39'),
(16, 'PG4422', 'ENTRADA', 15, 'Movimineto inicial', '2026-04-15 18:02:00'),
(17, 'PG1114', 'ENTRADA', 12, 'Movimineto inicial', '2026-04-15 18:02:46'),
(18, 'PG4427', 'ENTRADA', 700, 'Movimineto inicial', '2026-04-15 18:03:34'),
(19, 'PG4417', 'ENTRADA', 150, 'Movimineto inicial', '2026-04-15 18:04:47'),
-- (20, 'PG4423', 'ENTRADA', 12, 'Movimineto inicial', '2026-04-15 18:05:34'),
(21, 'PG449', 'ENTRADA', 7, 'Movimineto inicial', '2026-04-15 18:06:00'),
(22, 'PG4436', 'ENTRADA', 15, 'Movimiento inicial', '2026-04-15 18:06:53'),
(23, 'PG4419', 'ENTRADA', 3, 'Movimiento inicial', '2026-04-15 18:07:14'),
(24, 'PG4419', 'ENTRADA', 2, 'Movimiento inicial', '2026-04-15 18:08:17'),
(25, 'PG1111', 'ENTRADA', 7, 'Movimiento inicial', '2026-04-15 18:08:43'),
(26, 'PG4429', 'ENTRADA', 25, 'Movimiento inicial', '2026-04-15 18:09:08'),
(27, 'PG1112', 'ENTRADA', 15, 'Movimiento inicial', '2026-04-15 18:09:37'),
(28, 'PG4439', 'ENTRADA', 5, 'Movimiento inicial', '2026-04-15 18:11:40'),
(29, 'PG4428', 'ENTRADA', 700, 'Movimiento inicial', '2026-04-15 18:12:22'),
(30, 'PG4435', 'ENTRADA', 500, 'Movimiento inicial', '2026-04-15 18:12:43'),
(31, 'PG4438', 'ENTRADA', 7, 'Movimiento inicial', '2026-04-15 18:15:11'),
(32, 'PG4410', 'ENTRADA', 128, 'Movimiento inicial', '2026-04-15 18:17:17'),
(33, 'PG445', 'ENTRADA', 5, 'Movimiento inicial', '2026-04-15 18:18:23'),
(34, 'PG447', 'ENTRADA', 5, 'Movimiento inicial', '2026-04-15 18:18:52'),
(35, 'PG446', 'ENTRADA', 5, 'Movimiento inicial', '2026-04-15 18:19:15'),
(36, 'PG448', 'ENTRADA', 5, 'Movimiento inicial', '2026-04-15 18:19:38'),
(37, 'PG442', 'ENTRADA', 150, 'Movimiento inicial', '2026-04-15 18:20:40'),
(38, 'PG4424', 'ENTRADA', 240, 'Movimiento inicial', '2026-04-15 18:21:44'),
(39, 'PP223', 'ENTRADA', 240, 'Movimiento inicial', '2026-04-15 18:22:18'),
(40, 'PG4434', 'ENTRADA', 150, 'Movimiento inicial', '2026-04-15 18:23:12'),
(41, 'PP222', 'ENTRADA', 1000, 'Movimiento inicial', '2026-04-15 18:24:12'),
(42, 'PG444', 'ENTRADA', 8, 'Movimiento inicial', '2026-04-15 18:25:35'),
(43, 'PG4426', 'ENTRADA', 5, 'Movimiento inicial', '2026-04-15 18:26:05'),
(44, 'PU111', 'ENTRADA', 5, 'Movimiento inicial', '2026-04-15 18:27:54'),
(45, 'PG4432', 'ENTRADA', 20, 'Movimiento inicial', '2026-04-15 18:29:06'),

-- MOVIMIENTOS DE LOS COLORES
(46, 'ESM001', 'ENTRADA', 20.00, 'Movimiento inicial color', '2026-04-16 07:10:00'),
(47, 'ESM002', 'ENTRADA', 18.00, 'Movimiento inicial color', '2026-04-16 07:12:00'),
(48, 'ESM003', 'ENTRADA', 16.00, 'Movimiento inicial color', '2026-04-16 07:14:00'),
(49, 'ESM004', 'ENTRADA', 25.00, 'Movimiento inicial color', '2026-04-16 07:16:00'),
(50, 'ESM005', 'ENTRADA', 25.00, 'Movimiento inicial color', '2026-04-16 07:18:00');

-- INVENTARIO DE LOS COLORES
INSERT INTO inventario_producto (codigo_producto, stock_minimo, stock_maximo) VALUES
('ESM001', 10.00, 100.00),
('ESM002', 10.00, 100.00),
('ESM003', 10.00, 100.00),
('ESM004', 10.00, 100.00),
('ESM005', 10.00, 100.00);