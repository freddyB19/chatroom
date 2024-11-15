import settings 
from factory import create_app
from factory import create_app_socket


app = create_app(config_object = settings.configs['deploy'])
socketio = create_app_socket(app)


if __name__ == '__main__':
	socketio.run(app, use_reloader = True)

# gunicorn -b 127.0.0.1:5000 --worker-class eventlet app:app


