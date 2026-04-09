from app import create_app
from models import db, Usuario, Persona
from datetime import datetime

app = create_app()
with app.app_context():
    try:
        # 1. Creamos la Persona
        nueva_persona = Persona(
            nombre_persona="Beauty&Glam", 
            apellidos="Admin",
            telefono="1234567890",
            correo="admin@beautyglam.com",
            direccion="Calle Principal 12 A",
            # Asegúrate de que sea un objeto date o string válido según tu modelo
            fecha_nacimiento=datetime.strptime("1990-01-01", "%Y-%m-%d").date(),
            genero="Otro"
        )
        db.session.add(nueva_persona)
        
        # Hacemos flush para obtener el ID sin cerrar la transacción todavía
        db.session.flush() 

        # 2. Creamos el Usuario vinculado
        nuevo_usuario = Usuario(
            nombre_usuario="BeautyAdmin",
            id_persona=nueva_persona.id_persona,
            id_rol=1 
        )
        nuevo_usuario.set_password('Beauty&Glam')
        
        db.session.add(nuevo_usuario)
        
        # 3. Un solo commit para todo
        db.session.commit()
        print("¡Usuario administrador creado con éxito ya puedes ingresar con 'BeautyAdmin' y la contraseña 'Beauty&Glam'!")

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear el admin: {e}")