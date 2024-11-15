from flask import Flask

from flask_cors import CORS

from flask_socketio import SocketIO

from apps.chat import cache

from apps.chat.views import view as view_chat

from apps.chat.socket import ChatRoom
from apps.chat.socket import SalaDeEspera

def create_app(config_object):
	app = Flask(__name__)
	app.config.from_object(config_object)
	app.register_blueprint(view_chat)


	#
	cors = CORS(app, origins=['http:localhost:5000/'])

	#
	cache.init_app(app)

	return app


def create_app_socket(app):
	socket = SocketIO(app)

	socket.on_namespace(ChatRoom('/chat'))
	socket.on_namespace(SalaDeEspera('/sala-espera'))

	return socket


