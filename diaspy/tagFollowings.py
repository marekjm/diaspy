#!/usr/bin/env python3
from diaspy.models import FollowedTag
from diaspy import errors
class TagFollowings():
	"""This class represents the tags followed by the user.

	Should return `dict`s in a `list` with the following keys:
		`id`, `name`, `taggings_count`
	"""
	def __init__(self, connection, fetch=True):
		self._connection = connection
		self._tags = []
		if fetch: self.fetch()

	def __iter__(self): return iter(self._tags)

	def __getitem__(self, t): return self._tags[t]

	def _finalise(self, tags):
		return([FollowedTag(self._connection, t['id'], t['name'],
							t['taggings_count']) for t in tags])

	def fetch(self):
		"""(Re-)Fetches your followed tags.
		"""
		self._tags = self.get()

	def follow(self, name):
		"""Follows a tag by given name.

		Returns FollowedTag object.
		"""
		data = {'authenticity_token': repr(self._connection)}
		params = {'name': name}
		request = self._connection.post('tag_followings', data=data,
						params=params, headers={'accept': 'application/json'})
		if request.status_code != 201:
			raise errors.TagError('{0}: Tag could not be followed.'
							.format(request.status_code))
		result = request.json()
		self._tags.append(FollowedTag(self._connection, result['id'],
									result['name'], result['taggings_count']))
		return self._tags[(len(self._tags) - 1)]

	def get(self):
		request = self._connection.get('tag_followings.json')
		if request.status_code != 200:
			raise Exception('status code: {0}: cannot retreive tag_followings'
							.format(request.status_code))
		return self._finalise(request.json())
