from gevent import monkey
monkey.patch_all()

import settings 
from factory import create_app, create_app_socket


app = create_app(config_object = settings.configs['deploy'])
socketio = create_app_socket(app)
