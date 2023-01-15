from flask import Flask
from os import path
from flask_login import LoginManager

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = 'kjhsdadlaadsasdqwe'
    app.config.update(SESSION_COOKIE_SAMESITE='Lax')

    from .views import views 
    from .auth import auth
    
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')


    return app

