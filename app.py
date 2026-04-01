from flask import Flask, render_template, request, redirect, url_for, flash
from forms import UserForm
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask_migrate import Migrate
from models import db
from modulos.promociones import promociones
from modulos.procesoPago import proceso_pago
from modulos.reportes import reporte

app = Flask(__name__)
app.secret_key = "123456"
app.config.from_object(DevelopmentConfig)

app.register_blueprint(promociones)
app.register_blueprint(proceso_pago)
app.register_blueprint(reporte)

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    # REGISTRO DE BLUEPRINTS
    app.register_blueprint(acceso_bp)
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)