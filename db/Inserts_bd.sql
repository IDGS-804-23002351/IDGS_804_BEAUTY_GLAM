-- Insert into a la base de datos 
-- Rol
INSERT INTO rol(nombre_rol, descripcion) VALUES 
('Administrador','Acceso total a todos los modulos del sistema.'),
('Empleado','Gestion de citas y atencion al cliente.'),
('Cliente','Visualizacion de catalogos y citas personales,'),
('Proveedor','Vista de falta de inventario.');

-- Empresa
INSERT INTO empresa (rfc, nombre_empresa, direccion, contacto) VALUES 
('BEAUTY123456', 'Beauty Supply SA de CV', 'Av. Industrial 500, León, Gto.', 'contacto@beautysupply.com'),
('COSGLO98765', 'Cosméticos Glam SAPI', 'Calle Rosa 123, Zapopan, Jal.', 'ventas@cosmeticosglam.com'),
('DISBE456789', 'Distribuidora Bella', 'Blvd. Norte 789, Querétaro, Qro.', 'info@distribuidorabella.com'),
('LABBE321654', 'Laboratorios Beauty', 'Privada San José 45, Aguascalientes, Ags.', 'lab@beauty.com'),
('MAQPR111222', 'Maquillaje Pro', 'Av. Reforma 321, CDMX', 'ventas@maquillajepro.com'),
('PRODBE555666', 'Productos Bella', 'Calle Industria 78, Monterrey, NL', 'productos@bella.com'),
('SUPLY777888', 'Supply Cosmetics', 'Blvd. Los Angeles 222, Puebla, Pue.', 'supply@cosmetics.com'),
('FRAGAN999000', 'Fragancias y Más', 'Av. Primavera 111, Toluca, Mex.', 'fragancias@ymas.com'),
('CAPIL123444', 'Capil Beauty', 'Calle Salud 333, Guadalajara, Jal.', 'capil@beauty.com'),
('ESTET555777', 'Estética Pro', 'Av. Estética 456, San Luis Potosí, SLP', 'estetica@pro.com');

-- Puesto
INSERT INTO puesto (nombre_puesto) VALUES 
('Administrador'),
('Estilista'),
('Manicurista'),
('Pedicurista')
ON DUPLICATE KEY UPDATE nombre_puesto = VALUES(nombre_puesto);

-- servicios sin foto 
INSERT INTO servicio (nombre_servicio, precio, duracion_minutos, estatus, id_categoria) VALUES
('Uñas acrilicas', 500.00, 120, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria  = 'Uñas acrilicas' LIMIT 1)),
('Pedicure Spa curativo', 180.00, 40, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria  = 'Pedicure' LIMIT 1)),
('Shellac', 600.00, 120, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Uña natural' LIMIT 1)),
('Manicura Básica', 350.00, 80, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Manicure' LIMIT 1)),
('Pedicura Básica', 200.00, 40, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Pedicure' LIMIT 1)),
('Pedicura con estencion de uñas acrilicas', 400.00, 180, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Pedicure y uñas' LIMIT 1)),
('Uñas acrilicas XL', 350.00, 180, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Uñas acrilicas' LIMIT 1));

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
('Materia Prima'),
('Equipamiento'),
('Productos Terminados'),
('Servicios'),
('Papelería');

-- promociones
INSERT INTO promocion (nombre, tipo_promocion, descripcion, valor_descuento, foto, estatus) VALUES 
('Manos de Reina', 'Uñas acrilicas', 'Transforma tu estilo con un set de uñas acrílicas diseñado para destacar.', 12.00, 'promo1.jpg', 'ACTIVO'),
('Máximo Estilo XL', 'Uñas acrilicas XL', 'Luce un set de uñas acrílicas XL con el largo y diseño que siempre quisiste.', 30.00, 'promo2.jpg', 'ACTIVO'),
('Cumpleaños Glam', 'Manicura Básica', '¡Celebra tu día con nosotros! Disfruta de una manicura básica profesional para lucir unas manos impecables en tu mes especial.', 20.00, 'promo3.jpg', 'ACTIVO');