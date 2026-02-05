from typing import TypeVar

from flask_caching import Cache
from collections import defaultdict

SIMPLE_CACHE_CONFIG = {
	'CACHE_TYPE': 'SimpleCache',
	'CACHE_DEFAULT_TIMEOUT': 300,
}

config_cache = {
	'simple': SIMPLE_CACHE_CONFIG
}


cache = Cache(config = config_cache['simple'])

NAME_LIVINGROOM = "living-room"

Caching = TypeVar("Caching", bound=Cache)

def connect_to_livingroom(cache: Caching) -> None:
	TOTAL_ADD = 1
	
	if not cache.has('livingroom'):
		cache.set("livingroom", TOTAL_ADD)
	else:
		members = cache.get("livingroom")
		cache.set("livingroom", members + TOTAL_ADD)

def disconnect_to_livingroom(cache: Caching) -> None:
	if not cache.has('livingroom'):
		return None

	members = cache.get("livingroom")
	refresh_total_members = members - 1 if members > 0 else 1
	cache.set("livingroom", refresh_total_members)

def get_total_members_livingroom(cache: Caching) -> int:
	return cache.get("livingroom") if cache.has("livingroom") else 0

class Cache_UsersInRoom:
	def __init__(self, cache):
		self.cache = cache
		self.is_exists = True if self.cache.has('users_in_room') else False
		self.users_in_room = self.cache.get('users_in_room') if self.is_exists else {}

	def save_cache(self):
		self.cache.set('users_in_room', dict(self.users_in_room))
		self.is_exists = True

	def set_user_in_room(self, user, room):
		rooms = defaultdict(lambda: None, self.users_in_room)

		if rooms[room] is None:
			self.users_in_room[room] = [user]
		else:
			if user not in rooms[room]:
				users = rooms[room]
				users.append(user)
				rooms[room] = users

				self.users_in_room = rooms
		self.save_cache()


	def delete_user_in_room(self, user, room):
		if self.is_exists:
			rooms = defaultdict(lambda: None, self.users_in_room)

			if rooms[room] is not None:
				if user in rooms[room]:
					rooms[room] = [user_in_room for user_in_room in rooms[room] if user_in_room != user]


					if len(rooms[room]) == 0:
						rooms.pop(room)

					self.users_in_room = rooms

					self.save_cache()

	def get_users_in_room(self):
		if self.is_exists:

			rooms = defaultdict(lambda: [], self.users_in_room)

			if len(rooms.keys()) > 0:

				return [ 
					{'room': room, 'total_usuarios': len(usuarios)} 
					for room, usuarios in rooms.items()
				]

		return []

	def get_users_of_room(self, room):

		if self.is_exists:
			rooms = defaultdict(lambda: [], self.users_in_room)

			return rooms[room]
		return []
