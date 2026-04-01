from flask import Flask
from models import db
from modulos.acceso import acceso_bp
from config import Config
from modulos.usuarios import usuarios_bp 

def create_app():
    app = Flask(__name__)
    app.secret_key = "123456"
    app.config.from_object(Config)

    db.init_app(app)

    # REGISTRO DE BLUEPRINTS
    app.register_blueprint(acceso_bp)
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)