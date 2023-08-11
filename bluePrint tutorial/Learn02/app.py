from flask import Flask, render_template
from main.routes import main_bp
from about import about_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(main_bp)
    app.register_blueprint(about_bp, url_prefix='/about')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
