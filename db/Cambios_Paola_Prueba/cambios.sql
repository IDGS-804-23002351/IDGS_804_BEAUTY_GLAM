use salon_belleza;
-- Roll
INSERT INTO rol (nombre_rol) VALUES ('ADMINISTRADOR'), ('EMPLEADO'), ('CLIENTE')
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