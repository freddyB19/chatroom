import datetime

from flask import session

from flask_socketio import SocketIO
from flask_socketio import Namespace

from flask_socketio import emit
from flask_socketio import send
from flask_socketio import join_room
from flask_socketio import leave_room
from flask_socketio import disconnect
from flask_socketio import close_room


from . import cache
from . import Cache_UsersInRoom



class ConfigSalaEspera:
	NOMBRE_SALA_ESPERA = ('esRoom', )
	NAMESPACE_ROOM = ('/sala-espera', )

class CofigChatRoom:
	NAMESPACE_ROOM = ('/chat', )


class SalaDeEspera(Namespace, ConfigSalaEspera):

	def on_connect(self):
		print("Conectado al livingroom")
	
	def on_disconnect(self):
		print("Desconectado del livingroom")

		self.on_leave(data = {
			'room': ConfigSalaEspera.NOMBRE_SALA_ESPERA[0]
		})


	def on_join(self, data):
		cache_rooms = Cache_UsersInRoom(cache = cache)
		room:str = data['room']

		join_room(room)

		if room == self.NOMBRE_SALA_ESPERA[0]:
			rooms = cache_rooms.get_users_in_room()
			if rooms is not None:
				emit('sala_espera', {'rooms': rooms}, to=self.NOMBRE_SALA_ESPERA[0])

	def on_leave(self, data):
		room:str = data['room']

		if room == self.NOMBRE_SALA_ESPERA[0]:
			leave_room(room, namespace = ConfigSalaEspera.NAMESPACE_ROOM[0])



class ChatRoom(Namespace):
	def on_connect(self, data):
		print("Conectado al chat")

	def on_disconnect(self):
		print("Saliendo del chat")

		self.on_leave(data = {
			'username': session.get('request_username'), 
			'room': session.get('request_room'),
		})


	def on_join(self, data):
		cache_rooms = Cache_UsersInRoom(cache = cache)

		room:str = data['room']
		username:str = data['username']

		cache_rooms.set_user_in_room(room=room, user = username)
		lista_usuarios = cache_rooms.get_users_of_room(room = room)

		join_room(room, namespace=CofigChatRoom.NAMESPACE_ROOM[0])

		historial_mensajes:dict = cache.get(room)
		if historial_mensajes:
			emit('conectando', {"historial": historial_mensajes.copy()}, to=room)

		
		if username in lista_usuarios:
			
			context:dict = {
				'pin': {
					'mensaje': f'Se ha unido el usuario {username}', 
					'usuarios': len(lista_usuarios)
				}
			}

			emit('notificacion', context, to=room)

			rooms = cache_rooms.get_users_in_room()

			if rooms:
				emit('sala_espera', {'rooms': rooms}, namespace = ConfigSalaEspera.NAMESPACE_ROOM[0], broadcast = True)


	def on_leave(self, data):
		cache_rooms = Cache_UsersInRoom(cache = cache)

		room:str = data['room']
		username:str = data['username']
	
		cache_rooms.delete_user_in_room(room = room, user = username)
		lista_usuarios = cache_rooms.get_users_of_room(room = room)


		leave_room(room, namespace=CofigChatRoom.NAMESPACE_ROOM[0])

		if username not in lista_usuarios:

			emit(
				'notificacion', {
					'pin': {
						'mensaje': f'El usuario {username} ha salido del chat', 
						'usuarios': len(lista_usuarios)
					}},
				to=room
			)
			rooms = cache_rooms.get_users_in_room()

			if rooms:
				emit(
					'sala_espera', 
					{'rooms': rooms},
					namespace = ConfigSalaEspera.NAMESPACE_ROOM[0],
					broadcast = True
				)

			if len(lista_usuarios) == 0:
				cache.delete(room) # Eliminando historial de mensajes del chatroom

				close_room(room = room, namespace=CofigChatRoom.NAMESPACE_ROOM[0])

				
				
	def on_typing(self, data):
		room:str = data['room']
		username:str = data['username']
		typing:bool = data['typing']

		emit(
			'typing', 
			{'pin':{
				'username': username,
				'typing': typing,
				'mensaje': f'El usuario {username} esta escribiendo'
			}},
			to=room
		)

	def on_stopped_typing(self, data):
		room:str = data['room']

		username:str = data['username']
		typing:bool = data['typing']

		emit(
			'stopped_typing', 
			{'pin':{
				'username': username,
				'typing': typing,
				'mensaje': f'El usuario {username} ha dejado de escribir'
			}},
			to=room
		)

	def on_chat_mensaje(self, data):
		mensaje:str = data['mensaje']
		room:str = data['room']
		username:str = data['username']
		mensajes:list = list()

		tiempo:str = datetime.datetime.now().strftime("%I:%M %p %A")
				
		if cache.has(room):
			mensajes = cache.get(room)
		

		data_mensaje = {
			'mensaje': mensaje, 
			'tiempo': tiempo,
			'username': username
		}
		mensajes.append(data_mensaje)
		
		cache.set(room, mensajes)
		emit('mensaje', data_mensaje, to=room)
