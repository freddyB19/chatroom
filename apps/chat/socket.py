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

from . import (
	cache,
	NAME_LIVINGROOM,
	Cache_UsersInRoom,
	connect_to_livingroom,
	disconnect_to_livingroom,
	get_total_members_livingroom,
)


class ConfigSalaEspera:
	NOMBRE_SALA_ESPERA = NAME_LIVINGROOM
	NAMESPACE_ROOM = '/sala-espera'

class CofigChatRoom:
	NAMESPACE_ROOM = ('/chat', )


class SalaDeEspera(Namespace):
	
	def on_connect(self):
		connect_to_livingroom(cache)
	
	def on_disconnect(self):
		disconnect_to_livingroom(cache)

		self.on_leave(data = {
			'room': ConfigSalaEspera.NOMBRE_SALA_ESPERA
		})


	def on_join(self, data):
		cache_rooms = Cache_UsersInRoom(cache = cache)
		room:str = data['room']

		join_room(room)

		if room == ConfigSalaEspera.NOMBRE_SALA_ESPERA:
			rooms = cache_rooms.get_users_in_room()
			if rooms is not None:
				emit(
					'sala_espera', 
					{'rooms': rooms, 'total': get_total_members_livingroom(cache)}, 
					to=ConfigSalaEspera.NOMBRE_SALA_ESPERA
				)

	def on_leave(self, data):
		room:str = data['room']

		if room == ConfigSalaEspera.NOMBRE_SALA_ESPERA:
			leave_room(room, namespace = ConfigSalaEspera.NAMESPACE_ROOM)



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
					'total_usuarios': len(lista_usuarios),
					'usuarios': lista_usuarios
				}
			}

			emit('notificacion', context, to=room)

			rooms = cache_rooms.get_users_in_room()

			if rooms:
				emit(
					'sala_espera', 
					{'rooms': rooms, 'total': get_total_members_livingroom(cache)}, 
					namespace = ConfigSalaEspera.NAMESPACE_ROOM, 
					broadcast = True
				)


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
						'total_usuarios': len(lista_usuarios), 
						'usuarios': lista_usuarios
					}},
				to=room
			)
			rooms = cache_rooms.get_users_in_room()

			if rooms:
				emit(
					'sala_espera', 
					{'rooms': rooms, 'total': get_total_members_livingroom(cache)},
					namespace = ConfigSalaEspera.NAMESPACE_ROOM,
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
