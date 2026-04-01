from app import create_app
from models import db, Usuario, Persona

app = create_app()
with app.app_context():
    nueva_persona = Persona(
        nombre_persona="Jimena", 
        apellidos="Oropeza",
        correo="admin@beautyglam.com"
    )
    db.session.add(nueva_persona)
    db.session.commit()

    # 2. Creamos el Usuario vinculado a esa persona
    nuevo_usuario = Usuario(
        nombre_usuario="admin",
        id_persona=nueva_persona.id_persona,
        id_rol=1 # Asegúrate de que el rol 1 exista en tu tabla 'rol'
    )
    # Aquí se encripta la contraseña '12345'
    nuevo_usuario.set_password('12345')
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    print("¡Usuario administrador creado con éxito! Ya puedes loguearte con 'admin' y '12345'")