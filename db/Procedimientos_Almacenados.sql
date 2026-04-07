-- =====================================================
-- BASE DE DATOS SALON BELLEZA
-- SCRIPT COMPLETO CON TODOS LOS PROCEDIMIENTOS
-- =====================================================

USE salon_belleza;

-- =====================================================
-- CRUD DE CLIENTES
-- =====================================================

DELIMITER //

-- CREATE CLIENTE
CREATE PROCEDURE sp_crear_cliente(
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_nombre_usuario VARCHAR(100),
    IN p_contrasenia VARCHAR(255)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol_cliente INT;
    
    IF p_nombre IS NULL OR p_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre es obligatorio';
    END IF;
    
    IF p_apellidos IS NULL OR p_apellidos = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Los apellidos son obligatorios';
    END IF;
    
    IF p_correo IS NULL OR p_correo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo es obligatorio';
    END IF;
    
    IF p_correo NOT LIKE '%@%.%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El formato del correo no es valido';
    END IF;
    
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado';
    END IF;
    
    IF EXISTS(SELECT 1 FROM usuario WHERE nombre_usuario = p_nombre_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya esta en uso';
    END IF;
    
    IF p_contrasenia IS NULL OR p_contrasenia = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La contrasenia es obligatoria';
    END IF;
    
    IF LENGTH(p_contrasenia) < 6 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La contrasenia debe tener al menos 6 caracteres';
    END IF;
    
    START TRANSACTION;
    
    SELECT id_rol INTO v_id_rol_cliente FROM rol WHERE nombre_rol = 'CLIENTE';
    IF v_id_rol_cliente IS NULL THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El rol CLIENTE no existe en el sistema';
    END IF;
    
    INSERT INTO persona(nombre_persona, apellidos, telefono, correo, direccion)
    VALUES(p_nombre, p_apellidos, p_telefono, p_correo, p_direccion);
    SET v_id_persona = LAST_INSERT_ID();
    
    INSERT INTO usuario(nombre_usuario, contrasenia, id_persona, id_rol, estatus, intentos_fallidos, bloqueado)
    VALUES(p_nombre_usuario,SHA2(p_contrasenia,256), v_id_persona, v_id_rol_cliente, 'ACTIVO', 0, 0);
    SET v_id_usuario = LAST_INSERT_ID();
    
    INSERT INTO cliente(id_persona, id_usuario, estatus)
    VALUES(v_id_persona, v_id_usuario, 'ACTIVO');
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('CREAR CLIENTE', 'cliente', LAST_INSERT_ID(), v_id_usuario);
    
    COMMIT;
    
    SELECT 'Cliente creado exitosamente' as mensaje, LAST_INSERT_ID() as id_cliente;
    
END//

-- READ CLIENTE (por ID)
CREATE PROCEDURE sp_obtener_cliente(IN p_id_cliente INT)
BEGIN
    IF p_id_cliente IS NULL OR p_id_cliente <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del cliente no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM cliente WHERE id_cliente = p_id_cliente) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente no existe';
    END IF;
    
    SELECT 
        c.id_cliente,
        p.id_persona,
        p.nombre_persona,
        p.apellidos,
        p.telefono,
        p.correo,
        p.direccion,
        u.id_usuario,
        u.nombre_usuario,
        u.estatus as estatus_usuario,
        c.estatus as estatus_cliente,
        u.ultimo_acceso,
        u.bloqueado,
        COUNT(ct.id_cita) as total_citas
    FROM cliente c
    JOIN persona p ON c.id_persona = p.id_persona
    JOIN usuario u ON c.id_usuario = u.id_usuario
    LEFT JOIN cita ct ON c.id_cliente = ct.id_cliente
    WHERE c.id_cliente = p_id_cliente
    GROUP BY c.id_cliente;
    
END//

-- LISTAR CLIENTES
CREATE PROCEDURE sp_listar_clientes(
    IN p_estatus VARCHAR(10),
    IN p_buscar VARCHAR(100)
)
BEGIN
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('ACTIVO', 'INACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus debe ser ACTIVO o INACTIVO';
    END IF;
    
    SELECT 
        c.id_cliente,
        CONCAT(p.nombre_persona, ' ', p.apellidos) as nombre_completo,
        p.telefono,
        p.correo,
        c.estatus as estatus_cliente,
        u.nombre_usuario,
        COUNT(ct.id_cita) as total_citas
    FROM cliente c
    JOIN persona p ON c.id_persona = p.id_persona
    JOIN usuario u ON c.id_usuario = u.id_usuario
    LEFT JOIN cita ct ON c.id_cliente = ct.id_cliente
    WHERE (p_estatus IS NULL OR c.estatus = p_estatus)
    AND (p_buscar IS NULL OR 
         CONCAT(p.nombre_persona, ' ', p.apellidos) LIKE CONCAT('%', p_buscar, '%') OR
         p.telefono LIKE CONCAT('%', p_buscar, '%') OR
         p.correo LIKE CONCAT('%', p_buscar, '%'))
    GROUP BY c.id_cliente
    ORDER BY p.nombre_persona;
    
END//

-- UPDATE CLIENTE
CREATE PROCEDURE sp_actualizar_cliente(
    IN p_id_cliente INT,
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_estatus VARCHAR(10)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_estatus_actual VARCHAR(10);
    
    IF p_id_cliente IS NULL OR p_id_cliente <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del cliente no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM cliente WHERE id_cliente = p_id_cliente) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente no existe';
    END IF;
    
    IF p_nombre IS NULL OR p_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre es obligatorio';
    END IF;
    
    IF p_apellidos IS NULL OR p_apellidos = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Los apellidos son obligatorios';
    END IF;
    
    IF p_correo IS NULL OR p_correo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo es obligatorio';
    END IF;
    
    IF p_correo NOT LIKE '%@%.%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El formato del correo no es valido';
    END IF;
    
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    SELECT id_persona, id_usuario INTO v_id_persona, v_id_usuario 
    FROM cliente WHERE id_cliente = p_id_cliente;
    
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo AND id_persona != v_id_persona) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado por otro cliente';
    END IF;
    
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('ACTIVO', 'INACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus debe ser ACTIVO o INACTIVO';
    END IF;
    
    START TRANSACTION;
    
    SELECT estatus INTO v_estatus_actual FROM cliente WHERE id_cliente = p_id_cliente;
    
    UPDATE persona 
    SET nombre_persona = p_nombre,
        apellidos = p_apellidos,
        telefono = p_telefono,
        correo = p_correo,
        direccion = p_direccion
    WHERE id_persona = v_id_persona;
    
    UPDATE cliente SET estatus = p_estatus WHERE id_cliente = p_id_cliente;
    UPDATE usuario SET estatus = p_estatus WHERE id_usuario = v_id_usuario;
    
    IF v_estatus_actual != p_estatus THEN
        INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
        VALUES('cliente', p_id_cliente, v_estatus_actual, p_estatus);
    END IF;
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('ACTUALIZAR CLIENTE', 'cliente', p_id_cliente, v_id_usuario);
    
    COMMIT;
    
    SELECT 'Cliente actualizado exitosamente' as mensaje;
    
END//

-- DELETE CLIENTE (borrado lógico)
CREATE PROCEDURE sp_eliminar_cliente(IN p_id_cliente INT)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_estatus_actual VARCHAR(10);
    
    IF p_id_cliente IS NULL OR p_id_cliente <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del cliente no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM cliente WHERE id_cliente = p_id_cliente) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente no existe';
    END IF;
    
    IF EXISTS(SELECT 1 FROM cita 
              WHERE id_cliente = p_id_cliente 
              AND estatus IN ('PENDIENTE', 'CONFIRMADA')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar el cliente porque tiene citas pendientes o confirmadas';
    END IF;
    
    START TRANSACTION;
    
    SELECT id_persona, id_usuario, estatus INTO v_id_persona, v_id_usuario, v_estatus_actual
    FROM cliente WHERE id_cliente = p_id_cliente;
    
    UPDATE cliente SET estatus = 'INACTIVO' WHERE id_cliente = p_id_cliente;
    UPDATE usuario SET estatus = 'INACTIVO' WHERE id_usuario = v_id_usuario;
    
    INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
    VALUES('cliente', p_id_cliente, v_estatus_actual, 'INACTIVO');
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('ELIMINAR CLIENTE', 'cliente', p_id_cliente, v_id_usuario);
    
    COMMIT;
    
    SELECT 'Cliente eliminado (desactivado) exitosamente' as mensaje;
    
END//

-- =====================================================
-- CRUD DE EMPLEADOS
-- =====================================================

-- CREATE EMPLEADO
CREATE PROCEDURE sp_crear_empleado(
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_id_puesto INT,
    IN p_fecha_contratacion DATE,
    IN p_nombre_usuario VARCHAR(100),
    IN p_contrasenia VARCHAR(255)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol_empleado INT;
    DECLARE v_nombre_puesto VARCHAR(100);
    
    IF p_nombre IS NULL OR p_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre es obligatorio';
    END IF;
    
    IF p_apellidos IS NULL OR p_apellidos = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Los apellidos son obligatorios';
    END IF;
    
    IF p_correo IS NULL OR p_correo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo es obligatorio';
    END IF;
    
    IF p_correo NOT LIKE '%@%.%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El formato del correo no es valido';
    END IF;
    
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado';
    END IF;
    
    IF EXISTS(SELECT 1 FROM usuario WHERE nombre_usuario = p_nombre_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya esta en uso';
    END IF;
    
    IF p_contrasenia IS NULL OR LENGTH(p_contrasenia) < 6 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La contrasenia debe tener al menos 6 caracteres';
    END IF;
    
    IF p_fecha_contratacion IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de contratacion es obligatoria';
    END IF;
    
    IF p_fecha_contratacion > CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de contratacion no puede ser futura';
    END IF;
    
    IF p_id_puesto IS NULL OR p_id_puesto <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Debe seleccionar un puesto valido';
    END IF;
    
    SELECT nombre_puesto INTO v_nombre_puesto FROM puesto WHERE id_puesto = p_id_puesto;
    IF v_nombre_puesto IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El puesto seleccionado no existe en el catalogo';
    END IF;
    
    START TRANSACTION;
    
    SELECT id_rol INTO v_id_rol_empleado FROM rol WHERE nombre_rol = 'EMPLEADO';
    IF v_id_rol_empleado IS NULL THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El rol EMPLEADO no existe en el sistema';
    END IF;
    
    INSERT INTO persona(nombre_persona, apellidos, telefono, correo, direccion)
    VALUES(p_nombre, p_apellidos, p_telefono, p_correo, p_direccion);
    SET v_id_persona = LAST_INSERT_ID();
    
    INSERT INTO usuario(nombre_usuario, contrasenia, id_persona, id_rol, estatus, intentos_fallidos, bloqueado)
    VALUES(p_nombre_usuario,SHA2(p_contrasenia,256), v_id_persona, v_id_rol_empleado, 'ACTIVO', 0, 0);
    SET v_id_usuario = LAST_INSERT_ID();
    
    INSERT INTO empleado(fecha_contratacion, id_persona, id_puesto, id_usuario, estatus)
    VALUES(p_fecha_contratacion, v_id_persona, p_id_puesto, v_id_usuario, 'ACTIVO');
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('CREAR EMPLEADO', 'empleado', LAST_INSERT_ID(), v_id_usuario);
    
    COMMIT;
    
    SELECT CONCAT('Empleado creado exitosamente con puesto: ', v_nombre_puesto) as mensaje, 
           LAST_INSERT_ID() as id_empleado;
    
END//

-- READ EMPLEADO
CREATE PROCEDURE sp_obtener_empleado(IN p_id_empleado INT)
BEGIN
    IF p_id_empleado IS NULL OR p_id_empleado <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del empleado no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM empleado WHERE id_empleado = p_id_empleado) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no existe';
    END IF;
    
    SELECT 
        e.id_empleado,
        p.id_persona,
        p.nombre_persona,
        p.apellidos,
        p.telefono,
        p.correo,
        p.direccion,
        pu.id_puesto,
        pu.nombre_puesto,
        e.fecha_contratacion,
        e.estatus as estatus_empleado,
        u.id_usuario,
        u.nombre_usuario,
        u.estatus as estatus_usuario,
        u.ultimo_acceso
    FROM empleado e
    JOIN persona p ON e.id_persona = p.id_persona
    JOIN puesto pu ON e.id_puesto = pu.id_puesto
    JOIN usuario u ON e.id_usuario = u.id_usuario
    WHERE e.id_empleado = p_id_empleado;
    
END//

-- LISTAR EMPLEADOS
CREATE PROCEDURE sp_listar_empleados(
    IN p_estatus VARCHAR(10),
    IN p_id_puesto INT,
    IN p_buscar VARCHAR(100)
)
BEGIN
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('ACTIVO', 'INACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus debe ser ACTIVO o INACTIVO';
    END IF;
    
    IF p_id_puesto IS NOT NULL AND p_id_puesto > 0 THEN
        IF NOT EXISTS(SELECT 1 FROM puesto WHERE id_puesto = p_id_puesto) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El puesto seleccionado no existe';
        END IF;
    END IF;
    
    SELECT 
        e.id_empleado,
        CONCAT(p.nombre_persona, ' ', p.apellidos) as nombre_completo,
        p.telefono,
        p.correo,
        pu.nombre_puesto,
        e.fecha_contratacion,
        e.estatus as estatus_empleado,
        COUNT(DISTINCT ct.id_cita) as total_citas_atendidas,
        DATEDIFF(CURDATE(), e.fecha_contratacion) as dias_trabajados
    FROM empleado e
    JOIN persona p ON e.id_persona = p.id_persona
    JOIN puesto pu ON e.id_puesto = pu.id_puesto
    LEFT JOIN cita ct ON e.id_empleado = ct.id_empleado AND ct.estatus = 'FINALIZADA'
    WHERE (p_estatus IS NULL OR e.estatus = p_estatus)
    AND (p_id_puesto IS NULL OR p_id_puesto = 0 OR e.id_puesto = p_id_puesto)
    AND (p_buscar IS NULL OR 
         CONCAT(p.nombre_persona, ' ', p.apellidos) LIKE CONCAT('%', p_buscar, '%') OR
         p.telefono LIKE CONCAT('%', p_buscar, '%') OR
         p.correo LIKE CONCAT('%', p_buscar, '%'))
    GROUP BY e.id_empleado
    ORDER BY p.nombre_persona;
    
END//

-- UPDATE EMPLEADO
CREATE PROCEDURE sp_actualizar_empleado(
    IN p_id_empleado INT,
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_id_puesto INT,
    IN p_estatus VARCHAR(10)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_estatus_actual VARCHAR(10);
    DECLARE v_nombre_puesto VARCHAR(100);
    
    IF p_id_empleado IS NULL OR p_id_empleado <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del empleado no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM empleado WHERE id_empleado = p_id_empleado) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no existe';
    END IF;
    
    IF p_nombre IS NULL OR p_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre es obligatorio';
    END IF;
    
    IF p_apellidos IS NULL OR p_apellidos = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Los apellidos son obligatorios';
    END IF;
    
    IF p_correo IS NULL OR p_correo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo es obligatorio';
    END IF;
    
    IF p_correo NOT LIKE '%@%.%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El formato del correo no es valido';
    END IF;
    
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('ACTIVO', 'INACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus debe ser ACTIVO o INACTIVO';
    END IF;
    
    IF p_id_puesto IS NULL OR p_id_puesto <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Debe seleccionar un puesto valido';
    END IF;
    
    SELECT nombre_puesto INTO v_nombre_puesto FROM puesto WHERE id_puesto = p_id_puesto;
    IF v_nombre_puesto IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El puesto seleccionado no existe en el catalogo';
    END IF;
    
    START TRANSACTION;
    
    SELECT id_persona, id_usuario, estatus INTO v_id_persona, v_id_usuario, v_estatus_actual
    FROM empleado WHERE id_empleado = p_id_empleado;
    
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo AND id_persona != v_id_persona) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado por otro empleado';
    END IF;
    
    UPDATE persona 
    SET nombre_persona = p_nombre,
        apellidos = p_apellidos,
        telefono = p_telefono,
        correo = p_correo,
        direccion = p_direccion
    WHERE id_persona = v_id_persona;
    
    UPDATE empleado 
    SET id_puesto = p_id_puesto,
        estatus = p_estatus
    WHERE id_empleado = p_id_empleado;
    
    UPDATE usuario SET estatus = p_estatus WHERE id_usuario = v_id_usuario;
    
    IF v_estatus_actual != p_estatus THEN
        INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
        VALUES('empleado', p_id_empleado, v_estatus_actual, p_estatus);
    END IF;
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('ACTUALIZAR EMPLEADO', 'empleado', p_id_empleado, v_id_usuario);
    
    COMMIT;
    
    SELECT CONCAT('Empleado actualizado exitosamente. Nuevo puesto: ', v_nombre_puesto) as mensaje;
    
END//

-- DELETE EMPLEADO
CREATE PROCEDURE sp_eliminar_empleado(IN p_id_empleado INT)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_estatus_actual VARCHAR(10);
    
    IF p_id_empleado IS NULL OR p_id_empleado <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del empleado no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM empleado WHERE id_empleado = p_id_empleado) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no existe';
    END IF;
    
    IF EXISTS(SELECT 1 FROM cita 
              WHERE id_empleado = p_id_empleado 
              AND estatus IN ('PENDIENTE', 'CONFIRMADA')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar el empleado porque tiene citas pendientes o confirmadas';
    END IF;
    
    START TRANSACTION;
    
    SELECT id_persona, id_usuario, estatus INTO v_id_persona, v_id_usuario, v_estatus_actual
    FROM empleado WHERE id_empleado = p_id_empleado;
    
    UPDATE empleado SET estatus = 'INACTIVO' WHERE id_empleado = p_id_empleado;
    UPDATE usuario SET estatus = 'INACTIVO' WHERE id_usuario = v_id_usuario;
    
    INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
    VALUES('empleado', p_id_empleado, v_estatus_actual, 'INACTIVO');
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('ELIMINAR EMPLEADO', 'empleado', p_id_empleado, v_id_usuario);
    
    COMMIT;
    
    SELECT 'Empleado eliminado (desactivado) exitosamente' as mensaje;
    
END//

-- LISTAR PUESTOS
CREATE PROCEDURE sp_listar_puestos()
BEGIN
    SELECT id_puesto, nombre_puesto 
    FROM puesto 
    ORDER BY nombre_puesto;
END//

-- =====================================================
-- CRUD DE CITAS
-- =====================================================

-- CREATE CITA
CREATE PROCEDURE sp_crear_cita(
    IN p_id_cliente INT,
    IN p_id_empleado INT,
    IN p_fecha_hora DATETIME,
    IN p_servicios JSON
)
BEGIN
    DECLARE v_id_cita INT;
    DECLARE v_idx INT DEFAULT 0;
    DECLARE v_total_servicios INT;
    DECLARE v_id_servicio INT;
    DECLARE v_descuento DECIMAL(10,2);
    DECLARE v_precio_servicio DECIMAL(10,2);
    DECLARE v_subtotal DECIMAL(10,2);
    DECLARE v_duracion_total INT DEFAULT 0;
    DECLARE v_duracion_servicio INT;
    
    IF p_id_cliente IS NULL OR p_id_cliente <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ID cliente no valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM cliente WHERE id_cliente = p_id_cliente AND estatus = 'ACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cliente no existe o esta inactivo';
    END IF;
    
    IF p_id_empleado IS NULL OR p_id_empleado <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ID empleado no valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM empleado WHERE id_empleado = p_id_empleado AND estatus = 'ACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Empleado no existe o esta inactivo';
    END IF;
    
    IF p_fecha_hora IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Fecha y hora obligatoria';
    END IF;
    
    IF p_fecha_hora < NOW() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se pueden agendar citas en fechas pasadas';
    END IF;
    
    IF TIME(p_fecha_hora) < '09:00:00' OR TIME(p_fecha_hora) > '20:00:00' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Horario laboral 9:00 a 20:00';
    END IF;
    
    IF p_servicios IS NULL OR JSON_LENGTH(p_servicios) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Debe seleccionar al menos un servicio';
    END IF;
    
    START TRANSACTION;
    
    SET v_total_servicios = JSON_LENGTH(p_servicios);
    
    WHILE v_idx < v_total_servicios DO
        SET v_id_servicio = JSON_UNQUOTE(JSON_EXTRACT(p_servicios, CONCAT('$[', v_idx, '].id_servicio')));
        
        SELECT precio, duracion_minutos INTO v_precio_servicio, v_duracion_servicio
        FROM servicio 
        WHERE id_servicio = v_id_servicio AND estatus = 'ACTIVO';
        
        IF v_precio_servicio IS NULL THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un servicio no existe o esta inactivo';
        END IF;
        
        SET v_duracion_total = v_duracion_total + v_duracion_servicio;
        SET v_idx = v_idx + 1;
    END WHILE;
    
    IF EXISTS(
        SELECT 1 FROM cita 
        WHERE id_empleado = p_id_empleado 
        AND fecha_hora BETWEEN p_fecha_hora AND DATE_ADD(p_fecha_hora, INTERVAL v_duracion_total MINUTE)
        AND estatus IN ('PENDIENTE', 'CONFIRMADA')
    ) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Empleado no disponible en ese horario';
    END IF;
    
    IF EXISTS(
        SELECT 1 FROM cita 
        WHERE id_cliente = p_id_cliente 
        AND fecha_hora BETWEEN p_fecha_hora AND DATE_ADD(p_fecha_hora, INTERVAL v_duracion_total MINUTE)
        AND estatus IN ('PENDIENTE', 'CONFIRMADA')
    ) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cliente ya tiene cita en ese horario';
    END IF;
    
    INSERT INTO cita(fecha_hora, estatus, id_cliente, id_empleado)
    VALUES(p_fecha_hora, 'PENDIENTE', p_id_cliente, p_id_empleado);
    SET v_id_cita = LAST_INSERT_ID();
    
    SET v_idx = 0;
    WHILE v_idx < v_total_servicios DO
        SET v_id_servicio = JSON_UNQUOTE(JSON_EXTRACT(p_servicios, CONCAT('$[', v_idx, '].id_servicio')));
        SET v_descuento = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_servicios, CONCAT('$[', v_idx, '].descuento'))), 0);
        
        SELECT precio INTO v_precio_servicio FROM servicio WHERE id_servicio = v_id_servicio;
        SET v_subtotal = v_precio_servicio - v_descuento;
        
        IF v_descuento > v_precio_servicio THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Descuento no puede ser mayor al precio';
        END IF;
        
        INSERT INTO detalle_cita(id_cita, id_servicio, subtotal, descuento)
        VALUES(v_id_cita, v_id_servicio, v_subtotal, v_descuento);
        
        SET v_idx = v_idx + 1;
    END WHILE;
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado)
    VALUES('CREAR CITA', 'cita', v_id_cita);
    
    COMMIT;
    
    SELECT CONCAT('Cita creada ID: ', v_id_cita) AS mensaje, v_id_cita AS id_cita;
    
END//

-- READ CITA
CREATE PROCEDURE sp_obtener_cita(IN p_id_cita INT)
BEGIN
    IF p_id_cita IS NULL OR p_id_cita <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID de la cita no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM cita WHERE id_cita = p_id_cita) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita no existe';
    END IF;
    
    SELECT 
        ct.id_cita,
        ct.fecha_hora,
        ct.estatus as estatus_cita,
        ct.id_cliente,
        CONCAT(pc.nombre_persona, ' ', pc.apellidos) as nombre_cliente,
        pc.telefono as telefono_cliente,
        ct.id_empleado,
        CONCAT(pe.nombre_persona, ' ', pe.apellidos) as nombre_empleado,
        pu.nombre_puesto as puesto_empleado
    FROM cita ct
    JOIN cliente c ON ct.id_cliente = c.id_cliente
    JOIN persona pc ON c.id_persona = pc.id_persona
    JOIN empleado e ON ct.id_empleado = e.id_empleado
    JOIN persona pe ON e.id_persona = pe.id_persona
    LEFT JOIN puesto pu ON e.id_puesto = pu.id_puesto
    WHERE ct.id_cita = p_id_cita;
    
    SELECT 
        dc.id_detalle_cita,
        s.id_servicio,
        s.nombre_servicio,
        s.precio as precio_original,
        dc.descuento,
        dc.subtotal as precio_con_descuento,
        s.duracion_minutos
    FROM detalle_cita dc
    JOIN servicio s ON dc.id_servicio = s.id_servicio
    WHERE dc.id_cita = p_id_cita;
    
END//

-- LISTAR CITAS
CREATE PROCEDURE sp_listar_citas(
    IN p_estatus VARCHAR(20),
    IN p_id_cliente INT,
    IN p_id_empleado INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'FINALIZADA') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus no es valido';
    END IF;
    
    IF p_id_cliente IS NOT NULL AND p_id_cliente > 0 THEN
        IF NOT EXISTS(SELECT 1 FROM cliente WHERE id_cliente = p_id_cliente) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente no existe';
        END IF;
    END IF;
    
    IF p_id_empleado IS NOT NULL AND p_id_empleado > 0 THEN
        IF NOT EXISTS(SELECT 1 FROM empleado WHERE id_empleado = p_id_empleado) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no existe';
        END IF;
    END IF;
    
    IF p_fecha_inicio IS NOT NULL AND p_fecha_fin IS NOT NULL AND p_fecha_inicio > p_fecha_fin THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha inicio no puede ser mayor a la fecha fin';
    END IF;
    
    SELECT 
        ct.id_cita,
        ct.fecha_hora,
        DATE(ct.fecha_hora) as fecha,
        TIME(ct.fecha_hora) as hora,
        ct.estatus as estatus_cita,
        CONCAT(pc.nombre_persona, ' ', pc.apellidos) as cliente,
        CONCAT(pe.nombre_persona, ' ', pe.apellidos) as empleado,
        COUNT(dc.id_detalle_cita) as total_servicios,
        SUM(dc.subtotal) as total_cita
    FROM cita ct
    JOIN cliente c ON ct.id_cliente = c.id_cliente
    JOIN persona pc ON c.id_persona = pc.id_persona
    JOIN empleado e ON ct.id_empleado = e.id_empleado
    JOIN persona pe ON e.id_persona = pe.id_persona
    LEFT JOIN detalle_cita dc ON ct.id_cita = dc.id_cita
    WHERE (p_estatus IS NULL OR ct.estatus = p_estatus)
    AND (p_id_cliente IS NULL OR p_id_cliente = 0 OR ct.id_cliente = p_id_cliente)
    AND (p_id_empleado IS NULL OR p_id_empleado = 0 OR ct.id_empleado = p_id_empleado)
    AND (p_fecha_inicio IS NULL OR DATE(ct.fecha_hora) >= p_fecha_inicio)
    AND (p_fecha_fin IS NULL OR DATE(ct.fecha_hora) <= p_fecha_fin)
    GROUP BY ct.id_cita
    ORDER BY ct.fecha_hora DESC;
    
END//

-- ACTUALIZAR CITA
CREATE PROCEDURE sp_actualizar_cita(
    IN p_id_cita INT,
    IN p_fecha_hora DATETIME,
    IN p_id_empleado INT,
    IN p_estatus VARCHAR(20),
    IN p_servicios JSON
)
BEGIN
    DECLARE v_estatus_actual VARCHAR(20);
    DECLARE v_id_cliente INT;
    DECLARE v_id_empleado_actual INT;
    DECLARE v_fecha_hora_actual DATETIME;
    DECLARE v_duracion_total INT DEFAULT 0;
    DECLARE v_duracion_servicio INT;
    DECLARE v_idx INT DEFAULT 0;
    DECLARE v_total_servicios INT;
    DECLARE v_id_servicio INT;
    DECLARE v_descuento DECIMAL(10,2);
    DECLARE v_precio_servicio DECIMAL(10,2);
    DECLARE v_subtotal DECIMAL(10,2);
    DECLARE v_nueva_fecha_hora DATETIME;
    DECLARE v_nuevo_id_empleado INT;
    
    IF p_id_cita IS NULL OR p_id_cita <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID de la cita no es valido';
    END IF;
    
    SELECT estatus, id_cliente, id_empleado, fecha_hora 
    INTO v_estatus_actual, v_id_cliente, v_id_empleado_actual, v_fecha_hora_actual
    FROM cita WHERE id_cita = p_id_cita;
    
    IF v_estatus_actual IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita no existe';
    END IF;
    
    IF v_estatus_actual IN ('FINALIZADA', 'CANCELADA') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede modificar una cita finalizada o cancelada';
    END IF;
    
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'FINALIZADA') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus no es valido';
    END IF;
    
    START TRANSACTION;
    
    IF p_fecha_hora IS NULL THEN
        SET v_nueva_fecha_hora = v_fecha_hora_actual;
    ELSE
        SET v_nueva_fecha_hora = p_fecha_hora;
    END IF;
    
    IF p_id_empleado IS NULL THEN
        SET v_nuevo_id_empleado = v_id_empleado_actual;
    ELSE
        SET v_nuevo_id_empleado = p_id_empleado;
    END IF;
    
    IF p_fecha_hora IS NOT NULL OR p_id_empleado IS NOT NULL THEN
        
        IF NOT EXISTS(SELECT 1 FROM empleado WHERE id_empleado = v_nuevo_id_empleado AND estatus = 'ACTIVO') THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no existe o esta inactivo';
        END IF;
        
        IF v_nueva_fecha_hora < NOW() THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede reprogramar a una fecha pasada';
        END IF;
        
        IF TIME(v_nueva_fecha_hora) < '09:00:00' OR TIME(v_nueva_fecha_hora) > '20:00:00' THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita debe estar dentro del horario laboral';
        END IF;
        
        IF p_servicios IS NOT NULL AND JSON_LENGTH(p_servicios) > 0 THEN
            SET v_total_servicios = JSON_LENGTH(p_servicios);
            SET v_duracion_total = 0;
            SET v_idx = 0;
            
            WHILE v_idx < v_total_servicios DO
                SET v_id_servicio = JSON_UNQUOTE(JSON_EXTRACT(p_servicios, CONCAT('$[', v_idx, '].id_servicio')));
                
                SELECT duracion_minutos INTO v_duracion_servicio
                FROM servicio WHERE id_servicio = v_id_servicio;
                
                IF v_duracion_servicio IS NULL THEN
                    ROLLBACK;
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un servicio no existe';
                END IF;
                
                SET v_duracion_total = v_duracion_total + v_duracion_servicio;
                SET v_idx = v_idx + 1;
            END WHILE;
        ELSE
            SELECT IFNULL(SUM(s.duracion_minutos), 0) INTO v_duracion_total
            FROM detalle_cita dc
            JOIN servicio s ON dc.id_servicio = s.id_servicio
            WHERE dc.id_cita = p_id_cita;
        END IF;
        
        IF EXISTS(
            SELECT 1 FROM cita 
            WHERE id_cita != p_id_cita
            AND id_empleado = v_nuevo_id_empleado 
            AND fecha_hora BETWEEN v_nueva_fecha_hora AND DATE_ADD(v_nueva_fecha_hora, INTERVAL v_duracion_total MINUTE)
            AND estatus IN ('PENDIENTE', 'CONFIRMADA')
        ) THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no esta disponible en ese horario';
        END IF;
        
        IF EXISTS(
            SELECT 1 FROM cita 
            WHERE id_cita != p_id_cita
            AND id_cliente = v_id_cliente 
            AND fecha_hora BETWEEN v_nueva_fecha_hora AND DATE_ADD(v_nueva_fecha_hora, INTERVAL v_duracion_total MINUTE)
            AND estatus IN ('PENDIENTE', 'CONFIRMADA')
        ) THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente ya tiene una cita en ese horario';
        END IF;
        
        UPDATE cita 
        SET fecha_hora = v_nueva_fecha_hora,
            id_empleado = v_nuevo_id_empleado
        WHERE id_cita = p_id_cita;
    END IF;
    
    IF p_estatus IS NOT NULL AND p_estatus != v_estatus_actual THEN
        
        IF p_estatus = 'CANCELADA' AND v_estatus_actual = 'FINALIZADA' THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede cancelar una cita finalizada';
        END IF;
        
        IF p_estatus = 'FINALIZADA' AND v_estatus_actual != 'CONFIRMADA' THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se pueden finalizar citas confirmadas';
        END IF;
        
        UPDATE cita SET estatus = p_estatus WHERE id_cita = p_id_cita;
        
        INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
        VALUES('cita', p_id_cita, v_estatus_actual, p_estatus);
    END IF;
    
    IF p_servicios IS NOT NULL AND JSON_LENGTH(p_servicios) > 0 THEN
        DELETE FROM detalle_cita WHERE id_cita = p_id_cita;
        
        SET v_total_servicios = JSON_LENGTH(p_servicios);
        SET v_idx = 0;
        
        WHILE v_idx < v_total_servicios DO
            SET v_id_servicio = JSON_UNQUOTE(JSON_EXTRACT(p_servicios, CONCAT('$[', v_idx, '].id_servicio')));
            SET v_descuento = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(p_servicios, CONCAT('$[', v_idx, '].descuento'))), 0);
            
            SELECT precio INTO v_precio_servicio 
            FROM servicio 
            WHERE id_servicio = v_id_servicio AND estatus = 'ACTIVO';
            
            IF v_precio_servicio IS NULL THEN
                ROLLBACK;
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un servicio no existe o esta inactivo';
            END IF;
            
            IF v_descuento > v_precio_servicio THEN
                ROLLBACK;
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El descuento no puede ser mayor al precio';
            END IF;
            
            SET v_subtotal = v_precio_servicio - v_descuento;
            
            INSERT INTO detalle_cita(id_cita, id_servicio, subtotal, descuento)
            VALUES(p_id_cita, v_id_servicio, v_subtotal, v_descuento);
            
            SET v_idx = v_idx + 1;
        END WHILE;
    END IF;
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado)
    VALUES('ACTUALIZAR CITA', 'cita', p_id_cita);
    
    COMMIT;
    
    SELECT 'Cita actualizada exitosamente' AS mensaje;
    
END//

-- CANCELAR CITA
CREATE PROCEDURE sp_cancelar_cita(
    IN p_id_cita INT,
    IN p_motivo VARCHAR(255)
)
BEGIN
    DECLARE v_estatus_actual VARCHAR(20);
    DECLARE v_id_cliente INT;
    DECLARE v_fecha_hora DATETIME;
    
    IF p_id_cita IS NULL OR p_id_cita <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID de la cita no es valido';
    END IF;
    
    SELECT estatus, id_cliente, fecha_hora INTO v_estatus_actual, v_id_cliente, v_fecha_hora
    FROM cita WHERE id_cita = p_id_cita;
    
    IF v_estatus_actual IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita no existe';
    END IF;
    
    IF v_estatus_actual IN ('CANCELADA', 'FINALIZADA') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita ya esta cancelada o finalizada';
    END IF;
    
    START TRANSACTION;
    
    UPDATE cita SET estatus = 'CANCELADA' WHERE id_cita = p_id_cita;
    
    INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
    VALUES('cita', p_id_cita, v_estatus_actual, 'CANCELADA');
    
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado)
    VALUES('CANCELAR CITA', 'cita', p_id_cita);
    
    COMMIT;
    
    SELECT 'Cita cancelada exitosamente' AS mensaje;
    
END//

-- CONFIRMAR CITA
CREATE PROCEDURE sp_confirmar_cita(IN p_id_cita INT)
BEGIN
    DECLARE v_estatus_actual VARCHAR(20);
    
    IF p_id_cita IS NULL OR p_id_cita <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID de la cita no es valido';
    END IF;
    
    SELECT estatus INTO v_estatus_actual FROM cita WHERE id_cita = p_id_cita;
    
    IF v_estatus_actual IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita no existe';
    END IF;
    
    IF v_estatus_actual != 'PENDIENTE' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se pueden confirmar citas en estado PENDIENTE';
    END IF;
    
    START TRANSACTION;
    
    UPDATE cita SET estatus = 'CONFIRMADA' WHERE id_cita = p_id_cita;
    
    INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
    VALUES('cita', p_id_cita, v_estatus_actual, 'CONFIRMADA');
    
    COMMIT;
    
    SELECT 'Cita confirmada exitosamente' AS mensaje;
    
END//

-- FINALIZAR CITA
CREATE PROCEDURE sp_finalizar_cita(IN p_id_cita INT)
BEGIN
    DECLARE v_estatus_actual VARCHAR(20);
    DECLARE v_total DECIMAL(10,2);
    DECLARE v_id_pago INT;
    
    IF p_id_cita IS NULL OR p_id_cita <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID de la cita no es valido';
    END IF;
    
    SELECT estatus INTO v_estatus_actual FROM cita WHERE id_cita = p_id_cita;
    
    IF v_estatus_actual IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita no existe';
    END IF;
    
    IF v_estatus_actual != 'CONFIRMADA' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se pueden finalizar citas en estado CONFIRMADA';
    END IF;
    
    START TRANSACTION;
    
    SELECT SUM(subtotal) INTO v_total FROM detalle_cita WHERE id_cita = p_id_cita;
    
    INSERT INTO pago(fecha_pago, subtotal, impuesto, propina, total, id_cita)
    VALUES(NOW(), v_total, 0, 0, v_total, p_id_cita);
    
    SET v_id_pago = LAST_INSERT_ID();
    
    UPDATE cita SET estatus = 'FINALIZADA' WHERE id_cita = p_id_cita;
    
    INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
    VALUES('cita', p_id_cita, v_estatus_actual, 'FINALIZADA');
    
    COMMIT;
    
    SELECT CONCAT('Cita finalizada exitosamente. Total a pagar: $', v_total) as mensaje;
    
END//

-- CITAS POR CLIENTE
CREATE PROCEDURE sp_citas_por_cliente(IN p_id_cliente INT)
BEGIN
    IF p_id_cliente IS NULL OR p_id_cliente <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del cliente no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM cliente WHERE id_cliente = p_id_cliente) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente no existe';
    END IF;
    
    SELECT 
        ct.id_cita,
        ct.fecha_hora,
        ct.estatus,
        CONCAT(pe.nombre_persona, ' ', pe.apellidos) as empleado,
        COUNT(dc.id_detalle_cita) as num_servicios,
        SUM(dc.subtotal) as total
    FROM cita ct
    JOIN empleado e ON ct.id_empleado = e.id_empleado
    JOIN persona pe ON e.id_persona = pe.id_persona
    LEFT JOIN detalle_cita dc ON ct.id_cita = dc.id_cita
    WHERE ct.id_cliente = p_id_cliente
    GROUP BY ct.id_cita
    ORDER BY ct.fecha_hora DESC;
    
END//

-- DISPONIBILIDAD DE EMPLEADO
CREATE PROCEDURE sp_disponibilidad_empleado(
    IN p_id_empleado INT,
    IN p_fecha DATE
)
BEGIN
    IF p_id_empleado IS NULL OR p_id_empleado <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del empleado no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM empleado WHERE id_empleado = p_id_empleado AND estatus = 'ACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no existe o esta inactivo';
    END IF;
    
    SELECT 
        h.dia,
        h.hora_inicio,
        h.hora_fin,
        ct.fecha_hora as cita_programada,
        ct.estatus as estatus_cita,
        CONCAT(pc.nombre_persona, ' ', pc.apellidos) as cliente
    FROM horario h
    LEFT JOIN empleado_horario eh ON h.id_horario = eh.id_horario
    LEFT JOIN cita ct ON ct.id_empleado = p_id_empleado 
        AND DATE(ct.fecha_hora) = p_fecha
        AND ct.estatus IN ('PENDIENTE', 'CONFIRMADA')
    LEFT JOIN cliente c ON ct.id_cliente = c.id_cliente
    LEFT JOIN persona pc ON c.id_persona = pc.id_persona
    WHERE eh.id_empleado = p_id_empleado
    AND h.dia = DAYNAME(p_fecha)
    ORDER BY h.hora_inicio;
    
END//

DELIMITER ;

-- =====================================================
-- CRUD DE PROMOCIONES
-- =====================================================

DELIMITER //

/* 1. PROCEDIMIENTO PARA CREAR PROMOCIÓN */
CREATE PROCEDURE agregar_promocion(
    IN p_nombre VARCHAR(255),
    IN p_tipo VARCHAR(100),
    IN p_descripcion VARCHAR(255),
    IN p_valor DECIMAL(10,2),
    IN p_foto VARCHAR(255)
)
BEGIN
    INSERT INTO promocion (nombre, tipo_promocion, descripcion, valor_descuento, foto, estatus)
    VALUES (p_nombre, p_tipo, p_descripcion, p_valor, p_foto, 'ACTIVO');
END //

/* 2. PROCEDIMIENTO PARA ACTUALIZAR PROMOCIÓN */
CREATE PROCEDURE actualizar_promocion(
    IN p_id INT,
    IN p_nombre VARCHAR(255),
    IN p_tipo VARCHAR(100),
    IN p_descripcion VARCHAR(255),
    IN p_valor DECIMAL(10,2),
    IN p_foto VARCHAR(255)
)
BEGIN
    UPDATE promocion 
    SET nombre = p_nombre,
        tipo_promocion = p_tipo,
        descripcion = p_descripcion,
        valor_descuento = p_valor,
        foto = IF(p_foto IS NULL OR p_foto = '', foto, p_foto)
    WHERE id_promocion = p_id;
END //

/* 3. PROCEDIMIENTO PARA ELIMINACIÓN LÓGICA */
CREATE PROCEDURE eliminar_promocion(
    IN p_id INT
)
BEGIN
    UPDATE promocion 
    SET estatus = 'INACTIVO'
    WHERE id_promocion = p_id;
END //

DELIMITER ;

-- =====================================================
-- CRUD DE PROVEEDORES
-- =====================================================

DELIMITER //

-- CREATE PROVEEDOR
CREATE PROCEDURE sp_crear_proveedor(
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_rfc_empresa VARCHAR(13),
    IN p_id_tipo_proveedor INT
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_nombre_empresa VARCHAR(150);
    DECLARE v_tipo_proveedor VARCHAR(100);
    
    -- Validaciones de campos obligatorios
    IF p_nombre IS NULL OR p_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre es obligatorio';
    END IF;
    
    IF p_apellidos IS NULL OR p_apellidos = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Los apellidos son obligatorios';
    END IF;
    
    IF p_correo IS NULL OR p_correo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo es obligatorio';
    END IF;
    
    IF p_correo NOT LIKE '%@%.%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El formato del correo no es valido';
    END IF;
    
    -- Validación de teléfono (opcional pero con formato)
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    -- Validar que el correo no esté registrado
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado';
    END IF;
    
    -- Validar que la empresa exista
    IF p_rfc_empresa IS NOT NULL AND p_rfc_empresa != '' THEN
        SELECT nombre_empresa INTO v_nombre_empresa 
        FROM empresa WHERE rfc = p_rfc_empresa;
        
        IF v_nombre_empresa IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La empresa no existe en el sistema';
        END IF;
    END IF;
    
    -- Validar que el tipo de proveedor exista
    IF p_id_tipo_proveedor IS NULL OR p_id_tipo_proveedor <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Debe seleccionar un tipo de proveedor';
    END IF;
    
    SELECT tipo_proveedor INTO v_tipo_proveedor 
    FROM tipo_proveedor WHERE id_tipo_proveedor = p_id_tipo_proveedor;
    
    IF v_tipo_proveedor IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo de proveedor no existe';
    END IF;
    
    START TRANSACTION;
    
    -- Insertar persona
    INSERT INTO persona(nombre_persona, apellidos, telefono, correo, direccion)
    VALUES(p_nombre, p_apellidos, p_telefono, p_correo, p_direccion);
    SET v_id_persona = LAST_INSERT_ID();
    
    -- Insertar proveedor
    INSERT INTO proveedor(id_persona, rfc, id_tipo_proveedor, estatus)
    VALUES(v_id_persona, p_rfc_empresa, p_id_tipo_proveedor, 'ACTIVO');
    
    -- Registrar en bitácora
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado)
    VALUES('CREAR PROVEEDOR', 'proveedor', LAST_INSERT_ID());
    
    COMMIT;
    
    SELECT CONCAT('Proveedor creado exitosamente. Tipo: ', v_tipo_proveedor) as mensaje, 
           LAST_INSERT_ID() as id_proveedor;
    
END//

-- READ PROVEEDOR (por ID)
CREATE PROCEDURE sp_obtener_proveedor(IN p_id_proveedor INT)
BEGIN
    IF p_id_proveedor IS NULL OR p_id_proveedor <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del proveedor no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM proveedor WHERE id_proveedor = p_id_proveedor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor no existe';
    END IF;
    
    SELECT 
        p.id_proveedor,
        pe.id_persona,
        pe.nombre_persona,
        pe.apellidos,
        CONCAT(pe.nombre_persona, ' ', pe.apellidos) as nombre_completo,
        pe.telefono,
        pe.correo,
        pe.direccion,
        p.rfc as rfc_empresa,
        e.nombre_empresa,
        p.id_tipo_proveedor,
        tp.tipo_proveedor,
        p.estatus as estatus_proveedor,
        COUNT(DISTINCT cp.id_compra_proveedor) as total_compras,
        IFNULL(SUM(cp.total), 0) as total_gastado
    FROM proveedor p
    JOIN persona pe ON p.id_persona = pe.id_persona
    JOIN tipo_proveedor tp ON p.id_tipo_proveedor = tp.id_tipo_proveedor
    LEFT JOIN empresa e ON p.rfc = e.rfc
    LEFT JOIN compra_proveedor cp ON p.id_proveedor = cp.id_proveedor
    WHERE p.id_proveedor = p_id_proveedor
    GROUP BY p.id_proveedor;
    
END//

-- LISTAR PROVEEDORES
CREATE PROCEDURE sp_listar_proveedores(
    IN p_estatus VARCHAR(10),
    IN p_id_tipo_proveedor INT,
    IN p_buscar VARCHAR(100)
)
BEGIN
    -- Validaciones
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('ACTIVO', 'INACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus debe ser ACTIVO o INACTIVO';
    END IF;
    
    IF p_id_tipo_proveedor IS NOT NULL AND p_id_tipo_proveedor > 0 THEN
        IF NOT EXISTS(SELECT 1 FROM tipo_proveedor WHERE id_tipo_proveedor = p_id_tipo_proveedor) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo de proveedor no existe';
        END IF;
    END IF;
    
    SELECT 
        p.id_proveedor,
        CONCAT(pe.nombre_persona, ' ', pe.apellidos) as nombre_completo,
        pe.telefono,
        pe.correo,
        tp.tipo_proveedor,
        e.nombre_empresa as empresa_asociada,
        p.estatus as estatus_proveedor,
        COUNT(DISTINCT cp.id_compra_proveedor) as total_compras,
        IFNULL(SUM(cp.total), 0) as total_gastado
    FROM proveedor p
    JOIN persona pe ON p.id_persona = pe.id_persona
    JOIN tipo_proveedor tp ON p.id_tipo_proveedor = tp.id_tipo_proveedor
    LEFT JOIN empresa e ON p.rfc = e.rfc
    LEFT JOIN compra_proveedor cp ON p.id_proveedor = cp.id_proveedor
    WHERE (p_estatus IS NULL OR p.estatus = p_estatus)
    AND (p_id_tipo_proveedor IS NULL OR p_id_tipo_proveedor = 0 OR p.id_tipo_proveedor = p_id_tipo_proveedor)
    AND (p_buscar IS NULL OR 
         CONCAT(pe.nombre_persona, ' ', pe.apellidos) LIKE CONCAT('%', p_buscar, '%') OR
         pe.telefono LIKE CONCAT('%', p_buscar, '%') OR
         pe.correo LIKE CONCAT('%', p_buscar, '%') OR
         tp.tipo_proveedor LIKE CONCAT('%', p_buscar, '%'))
    GROUP BY p.id_proveedor
    ORDER BY pe.nombre_persona;
    
END//

-- UPDATE PROVEEDOR
CREATE PROCEDURE sp_actualizar_proveedor(
    IN p_id_proveedor INT,
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_rfc_empresa VARCHAR(13),
    IN p_id_tipo_proveedor INT,
    IN p_estatus VARCHAR(10)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_estatus_actual VARCHAR(10);
    DECLARE v_nombre_empresa VARCHAR(150);
    DECLARE v_tipo_proveedor VARCHAR(100);
    
    -- Validaciones básicas
    IF p_id_proveedor IS NULL OR p_id_proveedor <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del proveedor no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM proveedor WHERE id_proveedor = p_id_proveedor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor no existe';
    END IF;
    
    IF p_nombre IS NULL OR p_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre es obligatorio';
    END IF;
    
    IF p_apellidos IS NULL OR p_apellidos = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Los apellidos son obligatorios';
    END IF;
    
    IF p_correo IS NULL OR p_correo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo es obligatorio';
    END IF;
    
    IF p_correo NOT LIKE '%@%.%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El formato del correo no es valido';
    END IF;
    
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    IF p_estatus IS NOT NULL AND p_estatus NOT IN ('ACTIVO', 'INACTIVO') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El estatus debe ser ACTIVO o INACTIVO';
    END IF;
    
    -- Validar empresa
    IF p_rfc_empresa IS NOT NULL AND p_rfc_empresa != '' THEN
        SELECT nombre_empresa INTO v_nombre_empresa 
        FROM empresa WHERE rfc = p_rfc_empresa;
        
        IF v_nombre_empresa IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La empresa no existe en el sistema';
        END IF;
    END IF;
    
    -- Validar tipo proveedor
    IF p_id_tipo_proveedor IS NULL OR p_id_tipo_proveedor <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Debe seleccionar un tipo de proveedor';
    END IF;
    
    SELECT tipo_proveedor INTO v_tipo_proveedor 
    FROM tipo_proveedor WHERE id_tipo_proveedor = p_id_tipo_proveedor;
    
    IF v_tipo_proveedor IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo de proveedor no existe';
    END IF;
    
    START TRANSACTION;
    
    -- Obtener ID de persona
    SELECT id_persona, estatus INTO v_id_persona, v_estatus_actual
    FROM proveedor WHERE id_proveedor = p_id_proveedor;
    
    -- Validar correo duplicado
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo AND id_persona != v_id_persona) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado por otro proveedor';
    END IF;
    
    -- Actualizar persona
    UPDATE persona 
    SET nombre_persona = p_nombre,
        apellidos = p_apellidos,
        telefono = p_telefono,
        correo = p_correo,
        direccion = p_direccion
    WHERE id_persona = v_id_persona;
    
    -- Actualizar proveedor
    UPDATE proveedor 
    SET rfc = p_rfc_empresa,
        id_tipo_proveedor = p_id_tipo_proveedor,
        estatus = p_estatus
    WHERE id_proveedor = p_id_proveedor;
    
    -- Registrar cambio de estatus en historial
    IF v_estatus_actual != p_estatus THEN
        INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
        VALUES('proveedor', p_id_proveedor, v_estatus_actual, p_estatus);
    END IF;
    
    -- Registrar en bitácora
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado)
    VALUES('ACTUALIZAR PROVEEDOR', 'proveedor', p_id_proveedor);
    
    COMMIT;
    
    SELECT CONCAT('Proveedor actualizado exitosamente. Tipo: ', v_tipo_proveedor) as mensaje;
    
END//

-- DELETE PROVEEDOR (borrado lógico)
CREATE PROCEDURE sp_eliminar_proveedor(IN p_id_proveedor INT)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_estatus_actual VARCHAR(10);
    DECLARE v_total_compras INT;
    
    IF p_id_proveedor IS NULL OR p_id_proveedor <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del proveedor no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM proveedor WHERE id_proveedor = p_id_proveedor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor no existe';
    END IF;
    
    -- Verificar si tiene compras registradas
    SELECT COUNT(*) INTO v_total_compras 
    FROM compra_proveedor 
    WHERE id_proveedor = p_id_proveedor;
    
    IF v_total_compras > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar el proveedor porque tiene compras registradas. Considere desactivarlo en lugar de eliminarlo.';
    END IF;
    
    START TRANSACTION;
    
    -- Obtener información actual
    SELECT id_persona, estatus INTO v_id_persona, v_estatus_actual
    FROM proveedor WHERE id_proveedor = p_id_proveedor;
    
    -- Desactivar proveedor
    UPDATE proveedor SET estatus = 'INACTIVO' WHERE id_proveedor = p_id_proveedor;
    
    -- Registrar en historial
    INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
    VALUES('proveedor', p_id_proveedor, v_estatus_actual, 'INACTIVO');
    
    -- Registrar en bitácora
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado)
    VALUES('ELIMINAR PROVEEDOR', 'proveedor', p_id_proveedor);
    
    COMMIT;
    
    SELECT 'Proveedor desactivado exitosamente' as mensaje;
    
END//

-- =====================================================
-- PROCEDIMIENTOS ADICIONALES PARA PROVEEDORES
-- =====================================================

-- LISTAR TIPOS DE PROVEEDORES
CREATE PROCEDURE sp_listar_tipos_proveedor()
BEGIN
    SELECT id_tipo_proveedor, tipo_proveedor 
    FROM tipo_proveedor 
    ORDER BY tipo_proveedor;
END//

-- OBTENER COMPRAS POR PROVEEDOR
CREATE PROCEDURE sp_compras_por_proveedor(
    IN p_id_proveedor INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    IF p_id_proveedor IS NULL OR p_id_proveedor <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del proveedor no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM proveedor WHERE id_proveedor = p_id_proveedor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor no existe';
    END IF;
    
    IF p_fecha_inicio IS NOT NULL AND p_fecha_fin IS NOT NULL AND p_fecha_inicio > p_fecha_fin THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha inicio no puede ser mayor a la fecha fin';
    END IF;
    
    SELECT 
        cp.id_compra_proveedor,
        cp.fecha_compra,
        cp.total,
        COUNT(dc.id_detalle_compra) as numero_productos,
        SUM(dc.cantidad) as total_productos
    FROM compra_proveedor cp
    LEFT JOIN detalle_compra dc ON cp.id_compra_proveedor = dc.id_compra_proveedor
    WHERE cp.id_proveedor = p_id_proveedor
    AND (p_fecha_inicio IS NULL OR DATE(cp.fecha_compra) >= p_fecha_inicio)
    AND (p_fecha_fin IS NULL OR DATE(cp.fecha_compra) <= p_fecha_fin)
    GROUP BY cp.id_compra_proveedor
    ORDER BY cp.fecha_compra DESC;
    
END//

-- OBTENER PRODUCTOS POR PROVEEDOR
CREATE PROCEDURE sp_productos_por_proveedor(IN p_id_proveedor INT)
BEGIN
    IF p_id_proveedor IS NULL OR p_id_proveedor <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ID del proveedor no es valido';
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM proveedor WHERE id_proveedor = p_id_proveedor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor no existe';
    END IF;
    
    SELECT DISTINCT
        p.codigo_producto,
        p.nombre,
        p.precio_unitario,
        p.stock_actual,
        m.nombre_marca,
        um.nombre_unidad,
        COUNT(DISTINCT dc.id_detalle_compra) as veces_comprado,
        SUM(dc.cantidad) as total_adquirido
    FROM proveedor pr
    JOIN compra_proveedor cp ON pr.id_proveedor = cp.id_proveedor
    JOIN detalle_compra dc ON cp.id_compra_proveedor = dc.id_compra_proveedor
    JOIN producto p ON dc.codigo_producto = p.codigo_producto
    LEFT JOIN marca m ON p.id_marca = m.id_marca
    LEFT JOIN unidad_medida um ON p.id_unidad_medida = um.id_unidad_medida
    WHERE pr.id_proveedor = p_id_proveedor
    GROUP BY p.codigo_producto
    ORDER BY veces_comprado DESC;
    
END//

DELIMITER ;