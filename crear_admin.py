from app import create_app
from models import db, Usuario, Persona, Empleado
from datetime import datetime

app = create_app()
with app.app_context():
    try:
        nueva_persona = Persona(
            nombre_persona="Beauty&Glam", 
            apellidos="Admin",
            telefono="1234567890",
            correo="la.planta10s@gmail.com",
            direccion="Calle Principal 12 A",
            fecha_nacimiento=datetime.strptime("1990-01-01", "%Y-%m-%d").date(),
            genero="Otro"
        )
        db.session.add(nueva_persona)
        db.session.flush() # Obtenemos id_persona

        nuevo_usuario = Usuario(
            nombre_usuario="BeautyAdmin",
            id_persona=nueva_persona.id_persona,
            id_rol=1 
        )
        nuevo_usuario.set_password('12345678')
        db.session.add(nuevo_usuario)
        db.session.flush() 

        nuevo_empleado = Empleado(
            fecha_contratacion=datetime.now().date(),
            estatus='ACTIVO',
            id_persona=nueva_persona.id_persona,
            id_usuario=nuevo_usuario.id_usuario,
            id_puesto=1 
        )
        db.session.add(nuevo_empleado)
        
        db.session.commit()

        print("ÉXITO: Ya puedes loguearte como BeautyAdmin y password Beauty&Glam ya puedes agendar citas con este perfil.")

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear el registro completo: {e}")