from flask import Flask, render_template, request, redirect, url_for, flash
from forms import UserForm
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from models import db, Usuario
from flask_login import LoginManager
from config import DevelopmentConfig 

from modulos.promociones.routes import promociones
from modulos.procesoPago.routes import proceso_pago
from modulos.reportes.routes import reporte
from modulos.acceso.routes import acceso_bp
from modulos.usuarios.routes import usuarios_bp 
from modulos.bitacora.routes import bitacora_bp
from modulos.acceso.clientes import clientes
from modulos.acceso.empleados import empleado
from modulos.roles.routes import roles_bp  
from modulos.acceso.proveedores import proveedor

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(DevelopmentConfig)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.login_view = 'acceso.login' 
    login_manager.init_app(app)               

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    app.register_blueprint(promociones)
    app.register_blueprint(proceso_pago)
    app.register_blueprint(reporte)
    app.register_blueprint(acceso_bp)
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(bitacora_bp)
    app.register_blueprint(roles_bp, url_prefix='/roles')
    app.register_blueprint(clientes)
    app.register_blueprint(empleado)
    app.register_blueprint(proveedor)
    @app.errorhandler(404)
    
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.route('/')
    def index():
        return redirect(url_for('acceso.login'))
    
    @app.route('/clientes/formulario')
    def clientes_form():
        from forms import ClienteForm
        form = ClienteForm()
        return render_template('clientes/formclientes.html', form=form)
    
    @app.route('/empleados/formulario')
    def empleados_form():
        from forms import EmpleadoForm
        form = EmpleadoForm()
        return render_template('empleados/formempleados.html', form=form)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
