use salon_belleza;
DROP PROCEDURE IF EXISTS sp_crear_cliente;
DELIMITER //
CREATE PROCEDURE sp_crear_cliente(
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_nombre_usuario VARCHAR(100),
    IN p_contrasenia_hash VARCHAR(255),
    IN p_fecha_nacimiento DATE,
    IN p_genero VARCHAR(20)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol_cliente INT;
    
    -- Validaciones
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
    
    -- Validar fecha de nacimiento
    IF p_fecha_nacimiento IS NOT NULL THEN
        IF p_fecha_nacimiento > CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de nacimiento no puede ser futura';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) < 12 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente debe ser mayor de 12 años';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) > 120 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La edad ingresada no es valida';
        END IF;
    END IF;
    
    -- Validar género
    IF p_genero IS NOT NULL AND p_genero != '' THEN
        IF p_genero NOT IN ('Femenino', 'Masculino', 'Otro', 'Sin especificar') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El genero no es valido. Opciones: Femenino, Masculino, Otro, Sin especificar';
        END IF;
    END IF;
    
    -- Validación de existencia
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado';
    END IF;
    
    IF EXISTS(SELECT 1 FROM usuario WHERE nombre_usuario = p_nombre_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya esta en uso';
    END IF;
    
    -- Obtener rol CLIENTE
    SELECT id_rol INTO v_id_rol_cliente FROM rol WHERE nombre_rol = 'CLIENTE';
    IF v_id_rol_cliente IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El rol CLIENTE no existe en el sistema';
    END IF;
    
    START TRANSACTION;
    
    -- Insertar persona con nuevos campos
    INSERT INTO persona(nombre_persona, apellidos, telefono, correo, direccion, 
                       fecha_nacimiento, genero, ultima_actualizacion)
    VALUES(p_nombre, p_apellidos, p_telefono, p_correo, p_direccion, 
           p_fecha_nacimiento, COALESCE(p_genero, 'Sin especificar'), NOW());
    SET v_id_persona = LAST_INSERT_ID();
    
    -- Insertar usuario
    INSERT INTO usuario(nombre_usuario, contrasenia, id_persona, id_rol, estatus, intentos_fallidos, bloqueado)
    VALUES(p_nombre_usuario, p_contrasenia_hash, v_id_persona, v_id_rol_cliente, 'ACTIVO', 0, 0);
    SET v_id_usuario = LAST_INSERT_ID();
    
    -- Insertar cliente
    INSERT INTO cliente(id_persona, id_usuario, estatus)
    VALUES(v_id_persona, v_id_usuario, 'ACTIVO');
    
    COMMIT;
    
    SELECT 'Cliente registrado exitosamente' as mensaje, 
           LAST_INSERT_ID() as id_cliente;
    
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS sp_actualizar_cliente;

DELIMITER //

CREATE PROCEDURE sp_actualizar_cliente(
    IN p_id_cliente INT,
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_estatus VARCHAR(20),
    IN p_fecha_nacimiento DATE,
    IN p_genero VARCHAR(20)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_estatus_actual VARCHAR(20);
    
    -- Obtener id_persona del cliente
    SELECT id_persona, estatus INTO v_id_persona, v_estatus_actual
    FROM cliente 
    WHERE id_cliente = p_id_cliente;
    
    IF v_id_persona IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente no existe';
    END IF;
    
    -- Validaciones
    IF p_correo IS NOT NULL AND p_correo != '' THEN
        IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo AND id_persona != v_id_persona) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado por otro cliente';
        END IF;
    END IF;
    
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    -- Validar fecha de nacimiento
    IF p_fecha_nacimiento IS NOT NULL THEN
        IF p_fecha_nacimiento > CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de nacimiento no puede ser futura';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) < 12 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente debe ser mayor de 12 años';
        END IF;
    END IF;
    
    -- Validar género
    IF p_genero IS NOT NULL AND p_genero != '' THEN
        IF p_genero NOT IN ('Femenino', 'Masculino', 'Otro', 'Sin especificar') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El genero no es valido';
        END IF;
    END IF;
    
    START TRANSACTION;
    
    -- Actualizar persona
    UPDATE persona 
    SET nombre_persona = COALESCE(p_nombre, nombre_persona),
        apellidos = COALESCE(p_apellidos, apellidos),
        telefono = COALESCE(p_telefono, telefono),
        correo = COALESCE(p_correo, correo),
        direccion = COALESCE(p_direccion, direccion),
        fecha_nacimiento = COALESCE(p_fecha_nacimiento, fecha_nacimiento),
        genero = COALESCE(p_genero, genero),
        ultima_actualizacion = NOW()
    WHERE id_persona = v_id_persona;
    
    -- Actualizar cliente
    UPDATE cliente 
    SET estatus = COALESCE(p_estatus, estatus)
    WHERE id_cliente = p_id_cliente;
    
    COMMIT;
    
    SELECT 'Cliente actualizado exitosamente' as mensaje;
    
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS sp_obtener_cliente;
DELIMITER //
CREATE PROCEDURE sp_obtener_cliente(
    IN p_id_cliente INT
)
BEGIN
    SELECT 
        c.id_cliente,
        p.nombre_persona,
        p.apellidos,
        p.telefono,
        p.correo,
        p.direccion,
        c.estatus AS estatus_cliente,
        u.nombre_usuario,
        u.id_usuario,
        p.fecha_nacimiento,
        p.genero,
        DATE_FORMAT(p.fecha_nacimiento, '%Y-%m-%d') as fecha_nacimiento_formato,
        TIMESTAMPDIFF(YEAR, p.fecha_nacimiento, CURDATE()) as edad
    FROM cliente c
    INNER JOIN persona p ON c.id_persona = p.id_persona
    INNER JOIN usuario u ON c.id_usuario = u.id_usuario
    WHERE c.id_cliente = p_id_cliente;
END //

DELIMITER ;
DELIMITER //

CREATE PROCEDURE sp_eliminar_cliente(
    IN p_id_cliente INT
)
BEGIN
    DECLARE v_tiene_citas INT;
    
    -- Verificar si tiene citas pendientes
    SELECT COUNT(*) INTO v_tiene_citas
    FROM cita 
    WHERE id_cliente = p_id_cliente 
      AND estatus IN ('PENDIENTE', 'CONFIRMADA');
    
    IF v_tiene_citas > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'El cliente tiene citas pendientes o confirmadas';
    END IF;
    
    -- Desactivar cliente (borrado lógico)
    UPDATE cliente 
    SET estatus = 'INACTIVO'
    WHERE id_cliente = p_id_cliente;
    
    -- También desactivar el usuario asociado
    UPDATE usuario u
    INNER JOIN cliente c ON u.id_usuario = c.id_usuario
    SET u.estatus = 'INACTIVO'
    WHERE c.id_cliente = p_id_cliente;
    
    SELECT 'Cliente desactivado correctamente' as mensaje;
    
END //

DELIMITER ;
DELIMITER //

CREATE PROCEDURE sp_listar_clientes(
    IN p_estatus VARCHAR(20),
    IN p_buscar VARCHAR(100)
)
BEGIN
    SELECT 
        c.id_cliente,
        CONCAT(p.nombre_persona, ' ', p.apellidos) AS nombre_completo,
        p.telefono,
        p.correo,
        c.estatus AS estatus_cliente,
        u.nombre_usuario,
        (SELECT COUNT(*) FROM cita WHERE id_cliente = c.id_cliente) AS total_citas
    FROM cliente c
    INNER JOIN persona p ON c.id_persona = p.id_persona
    INNER JOIN usuario u ON c.id_usuario = u.id_usuario
    WHERE 
        -- Filtro por estatus: si es NULL o vacío o 'TODOS', no filtrar por estatus
        (p_estatus IS NULL OR p_estatus = '' OR p_estatus = 'TODOS' OR c.estatus = p_estatus)
        -- Filtro de búsqueda: si es NULL o vacío, no filtrar
        AND (p_buscar IS NULL OR p_buscar = '' OR 
             CONCAT(p.nombre_persona, ' ', p.apellidos) LIKE CONCAT('%', p_buscar, '%') OR 
             p.nombre_persona LIKE CONCAT('%', p_buscar, '%') OR
             p.apellidos LIKE CONCAT('%', p_buscar, '%') OR
             p.telefono LIKE CONCAT('%', p_buscar, '%') OR
             p.correo LIKE CONCAT('%', p_buscar, '%') OR
             u.nombre_usuario LIKE CONCAT('%', p_buscar, '%'))
    ORDER BY p.id_persona ASC;
    
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS sp_crear_empleado;
DELIMITER //

CREATE PROCEDURE sp_crear_empleado(
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_id_puesto INT,
    IN p_fecha_contratacion DATE,
    IN p_nombre_usuario VARCHAR(100),
    IN p_contrasenia_hash VARCHAR(255),
    IN p_fecha_nacimiento DATE,
    IN p_genero VARCHAR(20)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol_empleado INT;
    DECLARE v_nombre_puesto VARCHAR(100);
    
    -- Validaciones
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
    
    -- Validar fecha de nacimiento
    IF p_fecha_nacimiento IS NOT NULL THEN
        IF p_fecha_nacimiento > CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de nacimiento no puede ser futura';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) < 18 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado debe ser mayor de 18 años';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) > 70 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La edad ingresada supera el limite permitido';
        END IF;
    END IF;
    
    -- Validar género
    IF p_genero IS NOT NULL AND p_genero != '' THEN
        IF p_genero NOT IN ('Femenino', 'Masculino', 'Otro', 'Sin especificar') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El genero no es valido. Opciones: Femenino, Masculino, Otro, Sin especificar';
        END IF;
    END IF;
    
    -- Validación de existencia
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado';
    END IF;
    
    IF EXISTS(SELECT 1 FROM usuario WHERE nombre_usuario = p_nombre_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya esta en uso';
    END IF;
    
    IF p_contrasenia_hash IS NULL OR p_contrasenia_hash = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La contrasenia es obligatoria';
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
    
    -- Verificar puesto
    SELECT nombre_puesto INTO v_nombre_puesto FROM puesto WHERE id_puesto = p_id_puesto;
    IF v_nombre_puesto IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El puesto seleccionado no existe en el catalogo';
    END IF;
    
    -- Iniciar transacción
    START TRANSACTION;
    
    -- Obtener rol EMPLEADO
    SELECT id_rol INTO v_id_rol_empleado FROM rol WHERE nombre_rol = 'EMPLEADO';
    IF v_id_rol_empleado IS NULL THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El rol EMPLEADO no existe en el sistema';
    END IF;
    
    -- Insertar persona con nuevos campos
    INSERT INTO persona(nombre_persona, apellidos, telefono, correo, direccion,
                       fecha_nacimiento, genero, ultima_actualizacion)
    VALUES(p_nombre, p_apellidos, p_telefono, p_correo, p_direccion,
           p_fecha_nacimiento, COALESCE(p_genero, 'Sin especificar'), NOW());
    SET v_id_persona = LAST_INSERT_ID();
    
    -- Insertar usuario con contraseña encriptada
    INSERT INTO usuario(nombre_usuario, contrasenia, id_persona, id_rol, estatus, intentos_fallidos, bloqueado)
    VALUES(p_nombre_usuario, p_contrasenia_hash, v_id_persona, v_id_rol_empleado, 'ACTIVO', 0, 0);
    SET v_id_usuario = LAST_INSERT_ID();
    
    -- Insertar empleado
    INSERT INTO empleado(fecha_contratacion, id_persona, id_puesto, id_usuario, estatus)
    VALUES(p_fecha_contratacion, v_id_persona, p_id_puesto, v_id_usuario, 'ACTIVO');
    
    -- Insertar en bitácora
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('CREAR EMPLEADO', 'empleado', LAST_INSERT_ID(), v_id_usuario);
    
    COMMIT;
    
    SELECT CONCAT('Empleado creado exitosamente con puesto: ', v_nombre_puesto) AS mensaje, 
           LAST_INSERT_ID() AS id_empleado;
    
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS sp_actualizar_empleado;

DELIMITER //

CREATE PROCEDURE sp_actualizar_empleado(
    IN p_id_empleado INT,
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_id_puesto INT,
    IN p_estatus VARCHAR(10),
    IN p_fecha_nacimiento DATE,
    IN p_genero VARCHAR(20)
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
    
    -- Validar fecha de nacimiento
    IF p_fecha_nacimiento IS NOT NULL THEN
        IF p_fecha_nacimiento > CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de nacimiento no puede ser futura';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) < 18 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado debe ser mayor de 18 años';
        END IF;
    END IF;
    
    -- Validar género
    IF p_genero IS NOT NULL AND p_genero != '' THEN
        IF p_genero NOT IN ('Femenino', 'Masculino', 'Otro', 'Sin especificar') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El genero no es valido';
        END IF;
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
        direccion = p_direccion,
        fecha_nacimiento = COALESCE(p_fecha_nacimiento, fecha_nacimiento),
        genero = COALESCE(p_genero, genero),
        ultima_actualizacion = NOW()
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
    
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS sp_obtener_empleado;
DELIMITER //

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
        DATE_FORMAT(e.fecha_contratacion, '%Y-%m-%d') as fecha_contratacion_formato,
        e.estatus as estatus_empleado,
        u.id_usuario,
        u.nombre_usuario,
        u.estatus as estatus_usuario,
        u.ultimo_acceso,
        p.fecha_nacimiento,
        DATE_FORMAT(p.fecha_nacimiento, '%Y-%m-%d') as fecha_nacimiento_formato,
        p.genero,
        TIMESTAMPDIFF(YEAR, p.fecha_nacimiento, CURDATE()) as edad,
        p.ultima_actualizacion
    FROM empleado e
    JOIN persona p ON e.id_persona = p.id_persona
    JOIN puesto pu ON e.id_puesto = pu.id_puesto
    JOIN usuario u ON e.id_usuario = u.id_usuario
    WHERE e.id_empleado = p_id_empleado;
    
END //

DELIMITER ;

DELIMITER //
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
DELIMITER ;
DELIMITER //
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
    ORDER BY p.id_persona ASC;
    
END//
DELIMITER ;
DROP PROCEDURE IF EXISTS sp_crear_proveedor;

DELIMITER //

CREATE PROCEDURE sp_crear_proveedor(
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_rfc_empresa VARCHAR(13),
    IN p_id_tipo_proveedor INT,
    IN p_nombre_usuario VARCHAR(100),
    IN p_contrasenia_hash VARCHAR(255),
    IN p_fecha_nacimiento DATE,
    IN p_genero VARCHAR(20)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol_proveedor INT;
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
    
    -- Validación de teléfono
    IF p_telefono IS NOT NULL AND p_telefono != '' AND NOT (p_telefono REGEXP '^[0-9]{10}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El telefono debe tener 10 digitos numericos';
    END IF;
    
    -- Validar fecha de nacimiento
    IF p_fecha_nacimiento IS NOT NULL THEN
        IF p_fecha_nacimiento > CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de nacimiento no puede ser futura';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) < 18 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor debe ser mayor de 18 años';
        END IF;
    END IF;
    
    -- Validar género
    IF p_genero IS NOT NULL AND p_genero != '' THEN
        IF p_genero NOT IN ('Femenino', 'Masculino', 'Otro', 'Sin especificar') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El genero no es valido. Opciones: Femenino, Masculino, Otro, Sin especificar';
        END IF;
    END IF;
    
    -- Validar que el correo no esté registrado
    IF EXISTS(SELECT 1 FROM persona WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya esta registrado';
    END IF;
    
    -- Validar nombre de usuario
    IF EXISTS(SELECT 1 FROM usuario WHERE nombre_usuario = p_nombre_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya esta en uso';
    END IF;
    
    -- Validar contraseña
    IF p_contrasenia_hash IS NULL OR p_contrasenia_hash = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La contrasenia es obligatoria';
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
    
    -- Obtener rol PROVEEDOR
    SELECT id_rol INTO v_id_rol_proveedor FROM rol WHERE nombre_rol = 'PROVEEDOR';
    IF v_id_rol_proveedor IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El rol PROVEEDOR no existe en el sistema';
    END IF;
    
    START TRANSACTION;
    
    -- Insertar persona
    INSERT INTO persona(nombre_persona, apellidos, telefono, correo, direccion, 
                       fecha_nacimiento, genero, ultima_actualizacion)
    VALUES(p_nombre, p_apellidos, p_telefono, p_correo, p_direccion,
           p_fecha_nacimiento, COALESCE(p_genero, 'Sin especificar'), NOW());
    SET v_id_persona = LAST_INSERT_ID();
    
    -- Insertar usuario
    INSERT INTO usuario(nombre_usuario, contrasenia, id_persona, id_rol, estatus, intentos_fallidos, bloqueado)
    VALUES(p_nombre_usuario, p_contrasenia_hash, v_id_persona, v_id_rol_proveedor, 'ACTIVO', 0, 0);
    SET v_id_usuario = LAST_INSERT_ID();
    
    -- Insertar proveedor
    INSERT INTO proveedor(id_persona, rfc, id_tipo_proveedor, estatus)
    VALUES(v_id_persona, p_rfc_empresa, p_id_tipo_proveedor, 'ACTIVO');
    
    -- Registrar en bitácora
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('CREAR PROVEEDOR', 'proveedor', LAST_INSERT_ID(), v_id_usuario);
    
    COMMIT;
    
    SELECT CONCAT('Proveedor creado exitosamente. Tipo: ', v_tipo_proveedor) as mensaje, 
           LAST_INSERT_ID() as id_proveedor;
    
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS sp_actualizar_proveedor;

DELIMITER //

CREATE PROCEDURE sp_actualizar_proveedor(
    IN p_id_proveedor INT,
    IN p_nombre VARCHAR(50),
    IN p_apellidos VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_direccion VARCHAR(255),
    IN p_rfc_empresa VARCHAR(13),
    IN p_id_tipo_proveedor INT,
    IN p_estatus VARCHAR(10),
    IN p_fecha_nacimiento DATE,
    IN p_genero VARCHAR(20)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
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
    
    -- Validar fecha de nacimiento
    IF p_fecha_nacimiento IS NOT NULL THEN
        IF p_fecha_nacimiento > CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de nacimiento no puede ser futura';
        END IF;
        
        IF TIMESTAMPDIFF(YEAR, p_fecha_nacimiento, CURDATE()) < 18 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor debe ser mayor de 18 años';
        END IF;
    END IF;
    
    -- Validar género
    IF p_genero IS NOT NULL AND p_genero != '' THEN
        IF p_genero NOT IN ('Femenino', 'Masculino', 'Otro', 'Sin especificar') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El genero no es valido';
        END IF;
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
    
    -- Obtener ID de persona y usuario
    SELECT id_persona, estatus INTO v_id_persona, v_estatus_actual
    FROM proveedor WHERE id_proveedor = p_id_proveedor;
    
    -- Obtener id_usuario
    SELECT id_usuario INTO v_id_usuario FROM usuario WHERE id_persona = v_id_persona;
    
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
        direccion = p_direccion,
        fecha_nacimiento = COALESCE(p_fecha_nacimiento, fecha_nacimiento),
        genero = COALESCE(p_genero, genero),
        ultima_actualizacion = NOW()
    WHERE id_persona = v_id_persona;
    
    -- Actualizar proveedor
    UPDATE proveedor 
    SET rfc = p_rfc_empresa,
        id_tipo_proveedor = p_id_tipo_proveedor,
        estatus = p_estatus
    WHERE id_proveedor = p_id_proveedor;
    
    -- Actualizar estatus de usuario
    UPDATE usuario SET estatus = p_estatus WHERE id_usuario = v_id_usuario;
    
    -- Registrar cambio de estatus en historial
    IF v_estatus_actual != p_estatus THEN
        INSERT INTO historial_estatus(tabla_afectada, id_registro, estatus_anterior, estatus_nuevo)
        VALUES('proveedor', p_id_proveedor, v_estatus_actual, p_estatus);
    END IF;
    
    -- Registrar en bitácora
    INSERT INTO bitacora(accion, tabla_afectada, id_registro_afectado, id_usuario)
    VALUES('ACTUALIZAR PROVEEDOR', 'proveedor', p_id_proveedor, v_id_usuario);
    
    COMMIT;
    
    SELECT CONCAT('Proveedor actualizado exitosamente. Tipo: ', v_tipo_proveedor) as mensaje;
    
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS sp_obtener_proveedor;

DELIMITER //

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
        pe.fecha_nacimiento,
        pe.genero,
        p.rfc as rfc_empresa,
        e.nombre_empresa,
        p.id_tipo_proveedor,
        tp.tipo_proveedor,
        p.estatus as estatus_proveedor,
        u.id_usuario,
        u.nombre_usuario,
        (SELECT COUNT(*) FROM compra_proveedor WHERE id_proveedor = p.id_proveedor) as total_compras,
        (SELECT IFNULL(SUM(total), 0) FROM compra_proveedor WHERE id_proveedor = p.id_proveedor) as total_gastado
    FROM proveedor p
    JOIN persona pe ON p.id_persona = pe.id_persona
    JOIN tipo_proveedor tp ON p.id_tipo_proveedor = tp.id_tipo_proveedor
    LEFT JOIN empresa e ON p.rfc = e.rfc
    LEFT JOIN usuario u ON pe.id_persona = u.id_persona
    WHERE p.id_proveedor = p_id_proveedor;
    
END //

DELIMITER ;
DELIMITER //
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
DELIMITER ;
DELIMITER //
CREATE PROCEDURE sp_listar_tipos_proveedor()
BEGIN
    SELECT id_tipo_proveedor, tipo_proveedor 
    FROM tipo_proveedor 
    ORDER BY id_tipo_proveedor ASC;
END//
DELIMITER ;
DELIMITER //
CREATE PROCEDURE sp_listar_puestos()
BEGIN
    SELECT id_puesto, nombre_puesto 
    FROM puesto 
    ORDER BY id_puesto ASC;
END//
DELIMITER ;
DELIMITER //
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
    ORDER BY pe.id_persona ASC;
    
END//
DELIMITER ;