from flask import Flask, render_template
from main.routes import main_bp
from showSignUp import showSignUp_bp
from showAll_ATT import showAll_ATT_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(main_bp)
    app.register_blueprint(showSignUp_bp, url_prefix='/showSignUp')
    app.register_blueprint(showSignUp_bp, url_prefix='/showAll_ATT')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
