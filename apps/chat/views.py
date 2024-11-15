from flask import Blueprint

from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import render_template

from . import cache
from . import Cache_UsersInRoom



view = Blueprint('chat', __name__, template_folder = 'templates')

@view.before_request
def before():
	if request.endpoint == 'chat.index' and request.method == 'POST':
		session['request_username'] = request.form['username']
		session['request_room'] = request.form['nameChatroom']

	
@view.route("/", methods= ['GET', 'POST'])
def index():
	context = {}
	cache_rooms = Cache_UsersInRoom(cache = cache)

	if request.method == 'POST':
		room = request.form['nameChatroom']
		username = request.form['username']
		lista_usuarios = cache_rooms.get_users_of_room(room = room)

		if username not in lista_usuarios:
			context.update({
				'room': room,
			})
			return redirect(url_for('chat.chat_room', **context))

		context.update({
			'user': {
				'is_valid_username': False,
				'room': room,
				'username': username
			}
		})

	return render_template('index.html', **context)

@view.route("/chat-room/<room>", methods = ['GET'])
def chat_room(room:str=None):
	if session.get('request_username', False):
		context = {
			'name_room': room,
			'username': session['request_username']
		}

		return render_template('chat/chatroom.html', **context)
	return redirect(url_for('chat.index'))


@view.route("/salir-chat-room", methods = ['GET'])
def salir_chat():
	session.clear()
	return redirect(url_for('chat.index'))
