from flask import Blueprint, render_template

showSignUp_bp = Blueprint('showSignUp', __name__, template_folder='templates')

@showSignUp_bp.route('/')
def showSignUp():
    return render_template('showSignUp.html')
