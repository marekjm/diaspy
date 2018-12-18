#!/usr/bin/env python3


"""This module is only imported in other diaspy modules and
MUST NOT import anything.
"""


import json
import copy

BS4_SUPPORT=False
try:
	from bs4 import BeautifulSoup
except ImportError:
	import re
	print("[diaspy] BeautifulSoup not found, falling back on regex.")
else: BS4_SUPPORT=True

from diaspy import errors

class Aspect():
	"""This class represents an aspect.

	Class can be initialized by passing either an id and/or name as
	parameters.
	If both are missing, an exception will be raised.
	"""
	def __init__(self, connection, id, name=None):
		self._connection = connection
		self.id, self.name = id, name
		self._cached = []

	def getUsers(self, fetch = True):
		"""Returns list of GUIDs of users who are listed in this aspect.
		"""
		if fetch:
			request = self._connection.get('contacts.json?a_id={}'.format(self.id))
			self._cached = request.json()
		return self._cached

	def removeAspect(self):
		"""
		--> POST /aspects/{id} HTTP/1.1
		--> _method=delete&authenticity_token={token}

		<-- HTTP/1.1 302 Found

		Removes whole aspect.
		:returns: None
		"""
		request = self._connection.tokenFrom('contacts').delete('aspects/{}'.format(self.id))

		if request.status_code != 302:
			raise errors.AspectError('wrong status code: {0}'.format(request.status_code))

	def addUser(self, user_id):
		"""Add user to current aspect.

		:param user_id: user to add to aspect
		:type user_id: int
		:returns: JSON from request

		--> POST /aspect_memberships HTTP/1.1
		--> Accept: application/json, text/javascript, */*; q=0.01
		--> Content-Type: application/json; charset=UTF-8

		--> {"aspect_id":123,"person_id":123}

		<-- HTTP/1.1 200 OK
		"""
		data = {'aspect_id': self.id,
				'person_id': user_id}
		headers = {'content-type': 'application/json',
					'accept': 'application/json'}
		request = self._connection.tokenFrom('contacts').post('aspect_memberships', data=json.dumps(data), headers=headers)

		if request.status_code == 400:
			raise errors.AspectError('duplicate record, user already exists in aspect: {0}'.format(request.status_code))
		elif request.status_code == 404:
			raise errors.AspectError('user not found from this pod: {0}'.format(request.status_code))
		elif request.status_code != 200:
			raise errors.AspectError('wrong status code: {0}'.format(request.status_code))

		response = None
		try:
			response = request.json()
		except json.decoder.JSONDecodeError:
			""" Should be OK now, but I'll leave this commentary here 
			at first to see if anything comes up """
			# FIXME For some (?) reason removing users from aspects works, but
			# adding them is a no-go and Diaspora* kicks us out with CSRF errors.
			# Weird.
			pass

		if response is None:
			raise errors.CSRFProtectionKickedIn()

		# Now you should fetchguid(fetch_stream=False) on User to update aspect membership_id's
		# Or update it locally with the response
		return response

	def removeUser(self, user):
		"""Remove user from current aspect.

		:param user: user to remove from aspect
		:type user: diaspy.people.User object
		"""
		membership_id = None
		to_remove = None
		for each in user.aspectMemberships():
			if each.get('aspect', {}).get('id') == self.id:
				membership_id = each.get('id')
				to_remove = each
				break # no need to continue

		if membership_id is None:
			raise errors.UserIsNotMemberOfAspect(user, self)

		request = self._connection.delete('aspect_memberships/{0}'.format(membership_id))

		if request.status_code == 404:
			raise errors.AspectError('cannot remove user from aspect, probably tried too fast after adding: {0}'.format(request.status_code))

		elif request.status_code != 200:
			raise errors.AspectError('cannot remove user from aspect: {0}'.format(request.status_code))

		if 'contact' in user.data: # User object
			if to_remove: user.data['contact']['aspect_memberships'].remove( to_remove ) # remove local aspect membership_id
		else: # User object from Contacts()
			if to_remove: user.data['aspect_memberships'].remove( to_remove ) # remove local aspect membership_id
		return request.json()


class Notification():
	"""This class represents single notification.
	"""
	if not BS4_SUPPORT:
		_who_regexp = re.compile(r'/people/([0-9a-f]+)["\']{1} class=["\']{1}hovercardable')
		_aboutid_regexp = re.compile(r'/posts/[0-9a-f]+')
		_htmltag_regexp = re.compile('</?[a-z]+( *[a-z_-]+=["\'].*?["\'])* */?>')

	def __init__(self, connection, data):
		self._connection = connection
		self.type = data['type']
		self._data = data[self.type]
		self.id = self._data['id']
		self.unread = self._data['unread']

	def __getitem__(self, key):
		"""Returns a key from notification data.
		"""
		return self._data[key]

	def __str__(self):
		"""Returns notification note.
		"""
		if BS4_SUPPORT:
			soup = BeautifulSoup(self._data['note_html'], 'lxml')
			media_body = soup.find('div', {"class": "media-body"})
			div = media_body.find('div')
			if div: div.decompose()
			return media_body.getText().strip()
		else:
			string = re.sub(self._htmltag_regexp, '', self._data['note_html'])
			string = string.strip().split('\n')[0]
			while '  ' in string: string = string.replace('  ', ' ')
			return string

	def __repr__(self):
		"""Returns notification note with more details.
		"""
		return '{0}: {1}'.format(self.when(), str(self))

	def about(self):
		"""Returns id of post about which the notification is informing OR:
		If the id is None it means that it's about user so .who() is called.
		"""
		if BS4_SUPPORT:
			soup = BeautifulSoup(self._data['note_html'], 'lxml')
			id = soup.find('a', {"data-ref": True})
			if id: return id['data-ref']
			else: return self.who()[0]
		else:
			about = self._aboutid_regexp.search(self._data['note_html'])
			if about is None: about = self.who()[0]
			else: about = int(about.group(0)[7:])
			return about

	def who(self):
		"""Returns list of guids of the users who caused you to get the notification.
		"""
		if BS4_SUPPORT: # Parse the HTML with BS4
			soup = BeautifulSoup(self._data['note_html'], 'lxml')
			hovercardable_soup = soup.findAll('a', {"class": "hovercardable"})
			return list(set([soup['href'][8:] for soup in hovercardable_soup]))
		else:
			return list(set([who for who in self._who_regexp.findall(self._data['note_html'])]))

	def when(self):
		"""Returns UTC time as found in note_html.
		"""
		return self._data['created_at']

	def mark(self, unread=False):
		"""Marks notification to read/unread.
		Marks notification to read if `unread` is False.
		Marks notification to unread if `unread` is True.

		:param unread: which state set for notification
		:type unread: bool
		"""
		headers = {'x-csrf-token': repr(self._connection)}
		params = {'set_unread': json.dumps(unread)}
		response = self._connection.put('notifications/{0}'.format(self['id']), params=params, headers=headers)
		if response.status_code != 200:
			raise errors.NotificationError('Cannot mark notification: {0}'.format(response.status_code))
		self._data['unread'] = unread
		self.unread = unread


class Conversation():
	"""This class represents a conversation.

	.. note::
		Remember that you need to have access to the conversation.
	"""
	if not BS4_SUPPORT:
		_message_stream_regexp = re.compile(r'<div class=["\']{1}stream["\']{1}>(.*?)<div class=["\']{1}stream-element new-message["\']{1}>', re.DOTALL)
		_message_guid_regexp = re.compile(r'data-guid=["\']{1}([0-9]+)["\']{1}')
		_message_created_at_regexp = re.compile(r'<time datetime=["\']{1}([0-9]{4}-[0-9]{2}-[0-9]{1,2}T[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}Z)["\']{1}')
		_message_body_regexp = re.compile(r'<div class=["\']{1}message-content["\']{1}>\s+<p>(.*?)</p>\s+</div>', re.DOTALL)
		_message_author_guid_regexp = re.compile(r'<a href=["\']{1}/people/([a-f0-9]+)["\']{1} class=["\']{1}img')
		_message_author_name_regexp = re.compile(r'<img alt=["\']{1}(.*?)["\']{1}.*')
		_message_author_avatar_regexp = re.compile(r'src=["\']{1}(.*?)["\']{1}')
	def __init__(self, connection, id, fetch=True):
		"""
		:param conv_id: id of the post and not the guid!
		:type conv_id: str
		:param connection: connection object used to authenticate
		:type connection: connection.Connection
		"""
		self._connection = connection
		self.id = id
		self._data = {}
		self._messages = []
		if fetch: self._fetch()

	def __len__(self): return len(self._messages)
	def __iter__(self): return iter(self._messages)
	def __getitem__(self, n): return self._messages[n]

	def _fetch(self):
		"""Fetches JSON data representing conversation.
		"""
		request = self._connection.get('conversations/{}.json'.format(self.id))
		if request.status_code == 200:
			self._data = request.json()['conversation']
		else:
			raise errors.ConversationError('cannot download conversation data: {0}'.format(request.status_code))

	def _fetch_messages(self):
		"""Fetches HTML data we will use to parse message data.
		This is a workaround until Diaspora* has it's API plans implemented.
		"""
		request = self._connection.get('conversations/{}'.format(self.id))
		if request.status_code == 200:
			# Clear potential old messages
			self._messages = []

			message_template = {
					'guid'			: None,
					'created_at'	: None,
					'body'			: None,
					'author'		: {
						'guid'			: None,
						'diaspora_id'	: None, # TODO? Not able to get from this page.
						'name'			: None,
						'avatar'		: None
					}
			}

			if BS4_SUPPORT: # Parse the HTML with BS4
				soup = BeautifulSoup(request.content, 'lxml')
				messages_soup = soup.findAll('div', {"class": "stream-element message"})
				for message_soup in messages_soup:
					message = copy.deepcopy(message_template)

					# guid
					if message_soup and message_soup.has_attr('data-guid'):
						message['guid'] = message_soup['data-guid']

					# created_at
					time_soup = message_soup.find('time', {"class": "timeago"})
					if time_soup and time_soup.has_attr('datetime'):
						message['created_at'] = time_soup['datetime']

					# body
					body_soup = message_soup.find('div', {"class": "message-content"})
					if body_soup: message['body'] = body_soup.get_text().strip()

					# author
					author_a_soup = message_soup.find('a', {"class": "img"})
					if author_a_soup:
						# author guid
						message['author']['guid'] = author_a_soup['href'][8:]

						# name and avatar
						author_img_soup = author_a_soup.find('img', {"class": "avatar"})

						if author_img_soup:
							message['author']['name'] = author_img_soup['title']
							message['author']['avatar'] = author_img_soup['src']

					self._messages.append(message.copy())
			else: # Regex fallback
				messages_stream_html = self._message_stream_regexp.search(request.content.decode('utf-8'))
				if messages_stream_html:
					messages_html = messages_stream_html.group(1).split("<div class='stream-element message'")
					for message_html in messages_html:
						message = copy.deepcopy(message_template)

						# Guid
						guid = self._message_guid_regexp.search(message_html)
						if guid: message['guid'] = guid.group(1)
						else: continue

						# Created at
						created_at = self._message_created_at_regexp.search(message_html)
						if created_at: message['created_at'] = created_at.group(1)

						# Body
						body = self._message_body_regexp.search(message_html)
						if body: message['body'] = body.group(1)

						# Author
						author_guid = self._message_author_guid_regexp.search(message_html)
						if author_guid: message['author']['guid'] = author_guid.group(1)

						author_name = self._message_author_name_regexp.search(message_html)
						if author_name:
							message['author']['name'] = author_name.group(1)

							author_avatar = self._message_author_avatar_regexp.search(author_name.group(0))
							if author_avatar: message['author']['avatar'] = author_avatar.group(1)

						self._messages.append(message.copy())
		else:
			raise errors.ConversationError('cannot download message data from conversation: {0}'.format(request.status_code))

	def messages(self): return self._messages

	def update_messages(self):
		"""(Re-)fetches messages in this conversation.
		"""
		self._fetch_messages()

	def answer(self, text):
		"""Answer that conversation

		:param text: text to answer.
		:type text: str
		"""
		data = {'message[text]': text,
				'utf8': '&#x2713;',
				'authenticity_token': repr(self._connection)}

		request = self._connection.post('conversations/{}/messages'.format(self.id),
										data=data,
										headers={'accept': 'application/json'})
		if request.status_code != 200:
			raise errors.ConversationError('{0}: Answer could not be posted.'
										   .format(request.status_code))
		return request.json()

	def delete(self):
		"""Delete this conversation.
		Has to be implemented.
		"""
		data = {'authenticity_token': repr(self._connection)}

		request = self._connection.delete('conversations/{0}/visibility/'
								.format(self.id),
								data=data,
								headers={'accept': 'application/json'})

		if request.status_code != 404:
			raise errors.ConversationError('{0}: Conversation could not be deleted.'
										.format(request.status_code))

	def get_subject(self):
		"""Returns the subject of this conversation
		"""
		return self._data['subject']


class Comment():
	"""Represents comment on post.

	Does not require Connection() object. Note that you should not manually
	create `Comment()` objects -- they are designed to be created automatically
	by `Comments()` objects wich automatically will be created by `Post()` 
	objects.
	"""
	def __init__(self, data):
		self._data = data
		self.id = data['id']
		self.guid = data['guid']

	def __str__(self):
		"""Returns comment's text.
		"""
		return self._data['text']

	def __repr__(self):
		"""Returns comments text and author.
		Format: AUTHOR (AUTHOR'S GUID): COMMENT
		"""
		return '{0} ({1}): {2}'.format(self.author(), self.author('guid'), str(self))

	def when(self):
		"""Returns time when the comment had been created.
		"""
		return self._data['created_at']

	def author(self, key='name'):
		"""Returns author of the comment.
		"""
		return self._data['author'][key]

	def authordata(self):
		"""Returns all author data of the comment.
		"""
		return self._data['author']

class Comments():
	def __init__(self, comments=[]):
		self._comments = comments

	def __iter__(self):
		for comment in self._comments: yield comment

	def __len__(self):
		return len(self._comments)

	def __getitem__(self, index):
		if self._comments: return self._comments[index]

	def __bool__(self):
		if self._comments: return True
		return False

	def ids(self):
		return [c.id for c in self._comments]

	def delete(self, comment_id):
		for index, comment in enumerate(self._comments):
			if comment.id == comment_id:
				self._comments.pop(index);
				break;

	def add(self, comment):
		""" Expects Comment() object

		:param comment: Comment() object to add.
		:type comment: Comment() object."""
		if comment and type(comment) == Comment: self._comments.append(comment)

	def set(self, comments):
		"""Sets comments wich already have a Comment() obj

		:param comments: list with Comment() objects to set.
		:type comments: list.
		"""
		if comments: self._comments = comments

	def set_json(self, json_comments):
		"""Sets comments for this post from post data."""
		if json_comments:
			self._comments = [Comment(c) for c in json_comments]

class Post():
	"""This class represents a post.

	.. note::
		Remember that you need to have access to the post.
	"""
	def __init__(self, connection, id=0, guid='', fetch=True, comments=True, post_data=None):
		"""
		:param id: id of the post (GUID is recommended)
		:type id: int
		:param guid: GUID of the post
		:type guid: str
		:param connection: connection object used to authenticate
		:type connection: connection.Connection
		:param fetch: defines whether to fetch post's data or not
		:type fetch: bool
		:param comments: defines whether to fetch post's comments or not (if True also data will be fetched)
		:type comments: bool
		:param post_data: contains post data so no need to fetch the post if this is set, until you want to update post data
		:type: json
		"""
		if not (guid or id): raise TypeError('neither guid nor id was provided')
		self._connection = connection
		self.id = id
		self.guid = guid
		self._data = {}
		self.comments = Comments()
		if post_data: self._setdata(post_data)
		elif fetch: self._fetchdata()
		if comments:
			if not self._data: self._fetchdata()
			self._fetchcomments()

	def __repr__(self):
		"""Returns string containing more information then str().
		"""
		return '{0} ({1}): {2}'.format(self._data['author']['name'], self._data['author']['guid'], self._data['text'])

	def __str__(self):
		"""Returns text of a post.
		"""
		return self._data['text']

	def _setdata(self, data):
		self._data = data
		if not bool(self.comments) and data['interactions'].get('comments', []):
			self.comments.set_json(data['interactions'].get('comments', []))

	def _fetchdata(self):
		"""This function retrieves data of the post.

		:returns: guid of post whose data was fetched
		"""
		if self.id: id = self.id
		if self.guid: id = self.guid
		request = self._connection.get('posts/{0}.json'.format(id))
		if request.status_code != 200:
			raise errors.PostError('{0}: could not fetch data for post: {1}'.format(request.status_code, id))
		elif request: self._setdata(request.json());
		return self.data()['guid']

	def _fetchcomments(self):
		"""Retreives comments for this post.
		Retrieving comments via GUID will result in 404 error.
		DIASPORA* does not supply comments through /posts/:guid/ endpoint.
		"""
		id = self.data()['id']
		if self.data()['interactions']['comments_count']:
			request = self._connection.get('posts/{0}/comments.json'.format(id))
			if request.status_code != 200:
				raise errors.PostError('{0}: could not fetch comments for post: {1}'.format(request.status_code, id))
			else:
				self.comments.set([Comment(c) for c in request.json()])

	def _fetchlikes(self):
		id = self.data()['id']
		request = self._connection.get('posts/{0}/likes.json'.format(id))
		if request.status_code != 200:
			raise errors.PostError('{0}: could not fetch likes for post: {1}'.format(request.status_code, id))
		json = request.json();
		if json: self._data['interactions']['likes'] = request.json();
		return self._data['interactions']['likes'];

	def _fetchreshares(self):
		id = self.data()['id']
		request = self._connection.get('posts/{0}/reshares.json'.format(id))
		if request.status_code != 200:
			raise errors.PostError('{0}: could not fetch likes for post: {1}'.format(request.status_code, id))

		json = request.json();
		if json: self._data['interactions']['reshares'] = request.json();
		return self._data['interactions']['reshares'];

	def fetchlikes(self): return self._fetchlikes();
	def fetchreshares(self): return self._fetchreshares();

	def fetch(self, comments = False):
		"""Fetches post data.
		"""
		self._fetchdata()
		if comments: self._fetchcomments()
		return self

	def data(self, data = None):
		if data is not None:
			self._data = data
		return self._data

	def like(self):
		"""This function likes a post.
		It abstracts the 'Like' functionality.

		:returns: dict -- json formatted like object.
		"""
		data = {'authenticity_token': repr(self._connection)}

		request = self._connection.post('posts/{0}/likes'.format(self.id),	
										data=data,
										headers={'accept': 'application/json'})

		if request.status_code != 201:
			raise errors.PostError('{0}: Post could not be liked.'
								   .format(request.status_code))

		likes_json = request.json()
		if likes_json:
			self._data['interactions']['likes'].insert(0, likes_json)
			self._data['interactions']['likes_count'] = str(int(self._data['interactions']['likes_count'])+1)
		return likes_json

	def reshare(self):
		"""This function reshares a post
		"""
		data = {'root_guid': self._data['guid'],
				'authenticity_token': repr(self._connection)}

		request = self._connection.post('reshares',
										data=data,
										headers={'accept': 'application/json'})
		if request.status_code != 201:
			raise Exception('{0}: Post could not be reshared'.format(request.status_code))

		reshares_json = request.json()
		if reshares_json:
			self._data['interactions']['reshares'].insert(0, reshares_json)
			self._data['interactions']['reshares_count'] = str(int(self._data['interactions']['reshares_count'])+1)
		return request.json()

	def comment(self, text):
		"""This function comments on a post

		:param text: text to comment.
		:type text: str
		"""
		data = {'text': text,
				'authenticity_token': repr(self._connection)}
		request = self._connection.post('posts/{0}/comments'.format(self.id),
										data=data,
										headers={'accept': 'application/json'})

		if request.status_code != 201:
			raise Exception('{0}: Comment could not be posted.'
							.format(request.status_code))
		comment = Comment(request.json())
		self.comments.add(comment);
		return comment

	def vote_poll(self, poll_answer_id):
		"""This function votes on a post's poll

		:param poll_answer_id: id to poll vote.
		:type poll_answer_id: int
		"""
		poll_id = self._data['poll']['poll_id']
		data = {'poll_answer_id': poll_answer_id,
				'poll_id': poll_id,
				'post_id': self.id,
				'authenticity_token': repr(self._connection)}
		request = self._connection.post('posts/{0}/poll_participations'.format(self.id),
										data=data,
										headers={'accept': 'application/json'})
		if request.status_code != 201:
			raise Exception('{0}: Vote on poll failed.'
							.format(request.status_code))

		data = request.json()
		self._data["poll"]["participation_count"] += 1
		self._data["poll_participation_answer_id"] = data["poll_participation"]["poll_answer_id"]
		
		for answer in self._data["poll"]["poll_answers"]:
			if answer["id"] == poll_answer_id:
				answer["vote_count"] +=1;
				break;
		return data

	def hide(self):
		"""
		->	PUT /share_visibilities/42 HTTP/1.1
			  post_id=123
		<-	HTTP/1.1 200 OK
		"""
		headers = {'x-csrf-token': repr(self._connection)}
		params = {'post_id': json.dumps(self.id)}
		request = self._connection.put('share_visibilities/42', params=params, headers=headers)
		if request.status_code != 200:
			raise Exception('{0}: Failed to hide post.'
							.format(request.status_code))

	def mute(self):
		"""
		->	POST /blocks HTTP/1.1
			{"block":{"person_id":123}}
		<-	HTTP/1.1 204 No Content 
		"""
		headers = {'content-type':'application/json', 'x-csrf-token': repr(self._connection)}
		data = json.dumps({ 'block': { 'person_id' : self._data['author']['id'] } })
		request = self._connection.post('blocks', data=data, headers=headers)
		if request.status_code != 204:
			raise Exception('{0}: Failed to block person'
							.format(request.status_code))

	def subscribe(self):
		"""
		->	POST /posts/123/participation HTTP/1.1
		<-	HTTP/1.1 201 Created
		"""
		headers = {'x-csrf-token': repr(self._connection)}
		data = {}
		request = self._connection.post('posts/{}/participation'
							.format( self.id ), data=data, headers=headers)
		if request.status_code != 201:
			raise Exception('{0}: Failed to subscribe to post'
							.format(request.status_code))

		self._data.update({"participation" : True})

	def unsubscribe(self):
		"""
		->	POST /posts/123/participation HTTP/1.1
			  _method=delete
		<-	HTTP/1.1 200 OK
		"""
		headers = {'x-csrf-token': repr(self._connection)}
		data = { "_method": "delete" }
		request = self._connection.post('posts/{}/participation'
							.format( self.id ), headers=headers, data=data)
		if request.status_code != 200:
			raise Exception('{0}: Failed to unsubscribe to post'
							.format(request.status_code))

		self._data.update({"participation" : False})

	def report(self):
		"""
		TODO
		"""
		pass

	def delete(self):
		""" This function deletes this post
		"""
		data = {'authenticity_token': repr(self._connection)}
		request = self._connection.delete('posts/{0}'.format(self.id),
										  data=data,
										  headers={'accept': 'application/json'})
		if request.status_code != 204:
			raise errors.PostError('{0}: Post could not be deleted'.format(request.status_code))

	def delete_comment(self, comment_id):
		"""This function removes a comment from a post

		:param comment_id: id of the comment to remove.
		:type comment_id: str
		"""
		data = {'authenticity_token': repr(self._connection)}
		request = self._connection.delete('posts/{0}/comments/{1}'
										  .format(self.id, comment_id),
										  data=data,
										  headers={'accept': 'application/json'})

		if request.status_code != 204:
			raise errors.PostError('{0}: Comment could not be deleted'
								   .format(request.status_code))

		self.comments.delete(comment_id)

	def delete_like(self):
		"""This function removes a like from a post
		"""
		data = {'authenticity_token': repr(self._connection)}
		url = 'posts/{0}/likes/{1}'.format(self.id, self._data['interactions']['likes'][0]['id'])
		request = self._connection.delete(url, data=data)
		if request.status_code != 204:
			raise errors.PostError('{0}: Like could not be removed.'
								   .format(request.status_code))

		self._data['interactions']['likes'].pop(0);
		self._data['interactions']['likes_count'] = str(int(self._data['interactions']['likes_count'])-1)

	def author(self, key='name'):
		"""Returns author of the post.
		:param key: all keys available in data['author']
		"""
		return self._data['author'][key]

class FollowedTag():
	"""This class represents a followed tag.
	`diaspy.tagFollowings.TagFollowings()` uses it.
	"""
	def __init__(self, connection, id, name, taggings_count):
		self._connection = connection
		self._id, self._name, self._taggings_count = id, name, taggings_count

	def id(self): return self._id
	def name(self): return self._name
	def count(self): return self._taggings_count

	def delete(self):
		data = {'authenticity_token': repr(self._connection)}
		request = self._connection.delete('tag_followings/{0}'.format(self._id),
										data=data,
										headers={'accept': 'application/json'})
		if request.status_code != 204:
			raise errors.TagError('{0}: Tag could not be deleted.'
								   .format(request.status_code))
