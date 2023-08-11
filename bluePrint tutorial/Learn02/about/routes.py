from main import main_bp
from flask import render_template

about_bp = Blueprint('about', __name__, template_folder='templates')

@about_bp.route('/')
def about():
    return render_template('about.html')
