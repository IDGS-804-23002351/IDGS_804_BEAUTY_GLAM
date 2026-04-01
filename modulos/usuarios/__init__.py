from flask import Blueprint

# Definimos el blueprint para que Flask sepa que este módulo existe
usuarios_bp = Blueprint('usuarios', __name__, template_folder='templates')

from . import routes