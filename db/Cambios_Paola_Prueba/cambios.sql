use salon_belleza;
-- Roll
INSERT INTO rol (nombre_rol) VALUES ('ADMINISTRADOR'), ('EMPLEADO'), ('CLIENTE'),('PROVEEDOR')
ON DUPLICATE KEY UPDATE nombre_rol = VALUES(nombre_rol);

-- Insertar puestos 
INSERT INTO puesto (nombre_puesto) VALUES 
('Administrador'),
('Estilista'),
('Recepcionista')
ON DUPLICATE KEY UPDATE nombre_puesto = VALUES(nombre_puesto);

-- Crear empleado de prueba (ADMIN)
CALL sp_crear_empleado(
    'Admin',                    -- nombre
    'Sistema',                  -- apellidos
    '5551234567',              -- teléfono
    'admin@salonbelleza.com',  -- correo
    'Administracion',          -- dirección
    1,                         -- id_puesto (Administrador)
    CURDATE(),                 -- fecha_contratacion
    'admin',                   -- nombre_usuario
    'admin123'                 -- contraseña
);
select * from  cliente;
-- Probar el SP
CALL sp_listar_tipos_proveedor();
INSERT INTO tipo_proveedor (tipo_proveedor) VALUES 
('Materia Prima'),
('Equipamiento'),
('Productos Terminados'),
('Servicios'),
('Papelería');

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