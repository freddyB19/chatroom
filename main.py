
import settings 
from factory import create_app
from factory import create_app_socket


if __name__ == '__main__':
	setting = settings.configs['dev'] if settings.DEBUG else settings.configs['deploy']

	app = create_app(config_object = setting)
	socketio = create_app_socket(app)
	
	socketio.run(app, use_reloader = True, host=setting.HOST)