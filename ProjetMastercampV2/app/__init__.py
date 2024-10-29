from flask import Flask
from flask_socketio import SocketIO
from .routes import init_routes
from .events import init_socketio
import os


socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', os.urandom(24).hex())


    init_routes(app)

    socketio = SocketIO(app)
    init_socketio(socketio)

    return app, socketio