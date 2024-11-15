import settings 
from factory import create_app
from factory import create_app_socket

if __name__ == '__main__':
	app = create_app(config_object = settings.configs['dev'])
	socketio = create_app_socket(app)
	
	socketio.run(app, use_reloader = True)