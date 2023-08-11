from flask import Blueprint, render_template

showAll_ATT_bp = Blueprint('showAll_ATT', __name__, template_folder='templates')

@showAll_ATT_bp.route('/')
def showAll_ATT():
    return render_template('showAll_ATT.html')
