from app import create_app
from models import db, Usuario, Persona

app = create_app()
with app.app_context():
    nueva_persona = Persona(
        nombre_persona="Beauty&Glam", 
        apellidos="Admin",
        telefono="1234567890",
        correo="admin@beautyglam.com",
        direccion="Calle Principal 12 A"
    )
    db.session.add(nueva_persona)
    db.session.commit()

    # 2. Creamos el Usuario vinculado a esa persona
    nuevo_usuario = Usuario(
        nombre_usuario="BeautyAdmin",
        id_persona=nueva_persona.id_persona,
        id_rol=1 # Asegúrate de que el rol 1 exista en tu tabla 'rol'
    )
    # Aquí se encripta la contraseña 'Beauty&Glam'
    nuevo_usuario.set_password('Beauty&Glam')
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    print("¡Usuario administrador creado con éxito! Ya puedes loguearte con 'BeautyAdmin' y 'Beauty&Glam'")