import settings 
from factory import create_app
from factory import create_app_socket


app = create_app(config_object = settings.configs['deploy'])
socketio = create_app_socket(app)


