from flask import Blueprint

citas_bp = Blueprint(
    'citas_bp', 
    __name__, 
    template_folder='templates')
    
from . import routes