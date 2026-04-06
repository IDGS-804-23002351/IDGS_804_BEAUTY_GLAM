USE salon_belleza;

-- =====================================================
-- DATOS PARA LA AGENDA
-- =====================================================

-- 1. Verificar que los roles existen
SELECT * FROM rol;

-- 2. Verificar que el empleado admin se creó
SELECT * FROM empleado;
SELECT * FROM usuario WHERE nombre_usuario = 'admin';

-- 3. Crear CLIENTE de prueba (si no existe)
-- Primero verificar si ya existe el cliente
SET @cliente_exists = (SELECT COUNT(*) FROM cliente c 
                       JOIN persona p ON c.id_persona = p.id_persona 
                       WHERE p.correo = 'cliente@test.com');

IF @cliente_exists = 0 THEN
    -- Crear persona para cliente
    INSERT INTO persona (nombre_persona, apellidos, telefono, correo, direccion) 
    VALUES ('María', 'González Pérez', '5559876543', 'cliente@test.com', 'Calle Principal 123');
    
    SET @id_persona_cliente = LAST_INSERT_ID();
    SET @id_rol_cliente = (SELECT id_rol FROM rol WHERE nombre_rol = 'CLIENTE');
    
    -- Crear usuario para cliente
    INSERT INTO usuario (nombre_usuario, contrasenia, estatus, intentos_fallidos, bloqueado, id_persona, id_rol) 
    VALUES ('cliente', 'cliente123', 'ACTIVO', 0, 0, @id_persona_cliente, @id_rol_cliente);
    
    SET @id_usuario_cliente = LAST_INSERT_ID();
    
    -- Crear cliente
    INSERT INTO cliente (estatus, id_persona, id_usuario) 
    VALUES ('ACTIVO', @id_persona_cliente, @id_usuario_cliente);
    
    SELECT 'Cliente de prueba creado' as mensaje;
ELSE
    SELECT 'Cliente ya existe' as mensaje;
END IF;

-- 4. Crear EMPLEADO de prueba (si no existe)
SET @empleado_exists = (SELECT COUNT(*) FROM empleado e 
                        JOIN persona p ON e.id_persona = p.id_persona 
                        WHERE p.correo = 'empleado@test.com');

IF @empleado_exists = 0 THEN
    -- Crear persona para empleado
    INSERT INTO persona (nombre_persona, apellidos, telefono, correo, direccion) 
    VALUES ('Laura', 'Martínez López', '5554567890', 'empleado@test.com', 'Av. Trabajo 456');
    
    SET @id_persona_empleado = LAST_INSERT_ID();
    SET @id_rol_empleado = (SELECT id_rol FROM rol WHERE nombre_rol = 'EMPLEADO');
    SET @id_puesto_estilista = (SELECT id_puesto FROM puesto WHERE nombre_puesto = 'Estilista');
    
    -- Crear usuario para empleado
    INSERT INTO usuario (nombre_usuario, contrasenia, estatus, intentos_fallidos, bloqueado, id_persona, id_rol) 
    VALUES ('empleado', 'empleado123', 'ACTIVO', 0, 0, @id_persona_empleado, @id_rol_empleado);
    
    SET @id_usuario_empleado = LAST_INSERT_ID();
    
    -- Crear empleado
    INSERT INTO empleado (fecha_contratacion, estatus, id_persona, id_puesto, id_usuario) 
    VALUES (CURDATE(), 'ACTIVO', @id_persona_empleado, @id_puesto_estilista, @id_usuario_empleado);
    
    SELECT 'Empleado de prueba creado' as mensaje;
ELSE
    SELECT 'Empleado ya existe' as mensaje;
END IF;

-- 5. Crear SERVICIOS (si no existen)
INSERT IGNORE INTO servicio (nombre_servicio, precio, duracion_minutos, estatus, id_categoria) VALUES
('Corte de Cabello Dama', 250.00, 45, 'ACTIVO', (SELECT id_categoria FROM categoria LIMIT 1)),
('Corte de Cabello Caballero', 180.00, 30, 'ACTIVO', (SELECT id_categoria FROM categoria LIMIT 1)),
('Tinte Completo', 600.00, 120, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Coloración' LIMIT 1)),
('Manicura Básica', 150.00, 30, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Uñas' LIMIT 1)),
('Pedicura Básica', 200.00, 40, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Uñas' LIMIT 1)),
('Maquillaje Social', 400.00, 60, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Maquillaje' LIMIT 1)),
('Tratamiento Capilar', 350.00, 60, 'ACTIVO', (SELECT id_categoria FROM categoria WHERE nombre_categoria = 'Tratamientos Capilares' LIMIT 1));

-- 6. Crear MÉTODOS DE PAGO
INSERT IGNORE INTO metodo_pago (nombre_metodo) VALUES 
('Efectivo'),
('Tarjeta de Débito'),
('Tarjeta de Crédito');

-- 7. Crear HORARIOS
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

-- 9. Crear CITAS DE PRUEBA
-- Obtener IDs necesarios
SET @id_cliente = (SELECT id_cliente FROM cliente WHERE id_usuario = (SELECT id_usuario FROM usuario WHERE nombre_usuario = 'cliente'));
SET @id_empleado = (SELECT id_empleado FROM empleado WHERE id_usuario = (SELECT id_usuario FROM usuario WHERE nombre_usuario = 'empleado'));
SET @id_empleado_admin = (SELECT id_empleado FROM empleado WHERE id_usuario = (SELECT id_usuario FROM usuario WHERE nombre_usuario = 'admin'));

-- Insertar citas de prueba
INSERT INTO cita (fecha_hora, estatus, id_cliente, id_empleado) VALUES
(DATE_ADD(NOW(), INTERVAL 1 DAY), 'PENDIENTE', @id_cliente, @id_empleado),
(DATE_ADD(NOW(), INTERVAL 2 DAY), 'CONFIRMADA', @id_cliente, @id_empleado),
(DATE_ADD(NOW(), INTERVAL 3 DAY), 'PENDIENTE', @id_cliente, @id_empleado_admin),
(DATE_ADD(NOW(), INTERVAL 4 DAY), 'CONFIRMADA', @id_cliente, @id_empleado),
(DATE_ADD(NOW(), INTERVAL 5 DAY), 'FINALIZADA', @id_cliente, @id_empleado);

-- 10. Agregar detalles a las citas
-- Obtener IDs de servicios
SET @id_servicio_corte = (SELECT id_servicio FROM servicio WHERE nombre_servicio LIKE '%Corte%' LIMIT 1);
SET @id_servicio_manicura = (SELECT id_servicio FROM servicio WHERE nombre_servicio LIKE '%Manicura%' LIMIT 1);
SET @id_servicio_tinte = (SELECT id_servicio FROM servicio WHERE nombre_servicio LIKE '%Tinte%' LIMIT 1);
SET @id_servicio_pedicura = (SELECT id_servicio FROM servicio WHERE nombre_servicio LIKE '%Pedicura%' LIMIT 1);

-- Agregar detalles a las citas existentes
INSERT INTO detalle_cita (id_cita, id_servicio, subtotal, descuento)
SELECT c.id_cita, s.id_servicio, s.precio, 0
FROM cita c
CROSS JOIN (
    SELECT @id_servicio_corte as id_servicio, 250.00 as precio UNION ALL
    SELECT @id_servicio_manicura, 150.00
) s
WHERE c.id_cliente = @id_cliente 
AND c.id_cita = (SELECT MIN(id_cita) FROM cita WHERE id_cliente = @id_cliente)
ON DUPLICATE KEY UPDATE id_detalle_cita = id_detalle_cita;

-- =====================================================
-- VERIFICACIÓN DE DATOS
-- =====================================================

SELECT '=== USUARIOS ===' as '';
SELECT u.id_usuario, u.nombre_usuario, r.nombre_rol, u.estatus
FROM usuario u
JOIN rol r ON u.id_rol = r.id_rol
WHERE u.nombre_usuario IN ('admin', 'empleado', 'cliente');

SELECT '=== CLIENTES ===' as '';
SELECT c.id_cliente, CONCAT(p.nombre_persona, ' ', p.apellidos) as nombre, c.estatus
FROM cliente c
JOIN persona p ON c.id_persona = p.id_persona;

SELECT '=== EMPLEADOS ===' as '';
SELECT e.id_empleado, CONCAT(p.nombre_persona, ' ', p.apellidos) as nombre, pu.nombre_puesto, e.estatus
FROM empleado e
JOIN persona p ON e.id_persona = p.id_persona
JOIN puesto pu ON e.id_puesto = pu.id_puesto;

SELECT '=== SERVICIOS ===' as '';
SELECT id_servicio, nombre_servicio, precio, duracion_minutos
FROM servicio
WHERE estatus = 'ACTIVO'
LIMIT 5;

SELECT '=== CITAS ===' as '';
SELECT c.id_cita, c.fecha_hora, c.estatus, 
       CONCAT(pc.nombre_persona, ' ', pc.apellidos) as cliente,
       CONCAT(pe.nombre_persona, ' ', pe.apellidos) as empleado
FROM cita c
JOIN cliente cl ON c.id_cliente = cl.id_cliente
JOIN persona pc ON cl.id_persona = pc.id_persona
JOIN empleado e ON c.id_empleado = e.id_empleado
JOIN persona pe ON e.id_persona = pe.id_persona
ORDER BY c.fecha_hora;