from server import app
from unittest import TestCase, mock
import requests
from model import connect_to_db, db, example_data, Track
from flask import session


class FlaskTestsBasic(TestCase):
	""" Flask tests. """

	def setUp(self):
		""" Do before every test. """

		self.client = app.test_client()

		# Show Flask errors that occur during tests
		app.config['TESTING'] = True

		connect_to_db(app, "postgresql:///testdb")

		db.create_all()
		example_data()

	def tearDown(self):

		db.session.close()
		db.drop_all()


	def test_index(self):
		""" Test homepage. """

		result = self.client.get("/")
		self.assertIn(b'Sign In', result.data)


class FlaskTestsLoggedIn(TestCase):
	""" Tests for logged in vs not logged in. """

	def setUp(self):
		self.client = app.test_client()
		app.config['TESTING'] = True

		connect_to_db(app, "postgresql:///testdb")

		db.create_all()
		example_data()

		with self.client as c:
			with c.session_transaction() as sess:
				sess['username'] = 'HillaryForPres'

		self.client.post('/login',
						data={'username': 'HillaryForPres', 'password': 'bill123'},
						follow_redirects=True)


	def tearDown(self):

		db.session.close()
		db.drop_all()


	def test_show_playlists(self):
		""" Test show_playlist function. """

		result = self.client.get("/user")
		self.assertIn(b'<h3 class="title"> Playlists </h3>', result.data)


	def test_show_profile(self):
		""" Tests that profile page loads correctly for user. """

		result = self.client.get("/user", follow_redirects=True)
		self.assertIn(b'Hello, Hillary', result.data)


	def test_get_podcasts(self):
		""" Test handling iTunes API response. """
		# -------This doesn't require user to be logged in------
		# Move to tests basic
		pass


class FlaskTestsLogInLogOut(TestCase):
	""" Flask tests whether user login and logout function properly. """

	def setUp(self):
		""" Do before every test. """

		self.client = app.test_client()

		# Show Flask errors that occur during tests
		app.config['TESTING'] = True
		app.config['SECRET_KEY'] = 'MySecretKey'

		connect_to_db(app, "postgresql:///testdb")

		db.create_all()
		example_data()

	def tearDown(self):

		db.session.close()
		db.drop_all()


	def test_login(self):
		""" Test login form. """

		with self.client as c:
			result = c.post('/login',
							data={'username': 'HillaryForPres', 'password': 'bill123'},
							follow_redirects=True)
			self.assertEqual(session['username'], 'HillaryForPres')


	def test_logout(self):
		""" Test log out route. """

		result = self.client.post("/logout",
								  follow_redirects=True)
		self.assertNotIn(b'<a href="/user">Home</a>', result.data)


	def test_registration_form(self):
		""" Testing registration form route. """

		result = self.client.get("/registration", method='GET')
		self.assertIn(b'<form action="/registration" method="post">',
					  result.data)


	def test_register(self):
		""" Test that db updates to reflect new user. """

		result = self.client.post("/registration",
								 method='POST',
								 data={'username': 'henrythepup',
								 	   'fname': 'Henry',
								 	   'lname': 'Louise',
								 	   'email': 'henrypup@gmail.com',
								 	   'password': 'bonesforever'},
								 follow_redirects=True)

		self.assertIn(b'Sign In', result.data)


class FlaskTestsDatabase(TestCase):
	""" Flask tests using database. """

	def setUp(self):
		""" Set up and connect to testdb. """

		self.client = app.test_client()
		app.config['TESTING'] = True

		connect_to_db(app, 'postgresql:///testdb')

		db.create_all()
		example_data()

		with self.client as c:
			with c.session_transaction() as sess:
				sess['username'] = 'HillaryForPres'

		self.client.post('/login',
						data={'username': 'HillaryForPres', 'password': 'bill123'},
						follow_redirects=True)

	def tearDown(self):
		
		db.session.close()
		db.drop_all()


	def test_add_playlist(self):
		""" Test add playlist route. """

		result = self.client.post('/add-playlist',
								 data={'title': 'News'},
								 follow_redirects=True)
		self.assertIn(b'Playlist added', result.data)


	def test_add_track(self):
		""" Test add track route. """

		self.client.post('/add-playlist',
						 data={'title': 'News'})

		result = self.client.post('/add-track',
								  data={'artist': 'Mark Maron',
								  		'title': 'Some Interview',
								  		'rss': 'thisaudiofile.mp3',
								  		'playlist_title': 'News'},
								  follow_redirects=True)
		self.assertIn(b'Some Interview', result.data)


	def test_delete_track(self):

		self.client.post('/add-playlist',
						 data={'title': 'News'})

		self.client.post('/add-track',
						 data={'artist': 'Mark Maron',
						 'title': 'Some Interview',
						 'rss': 'thisaudiofile.mp3',
						 'playlist_title': 'News'})

		result = self.client.post('/delete-track',
								  data={'track_id': 3},
								  follow_redirects=True)

		self.assertNotIn(b'Some Interview', result.data)


	def test_search_users(self):

		result = self.client.get('/search-users',
								 data={'username': 'HappyTrees'},
								 follow_redirects=True)

		self.assertIn(b'HappyTrees', result.data)


	# def test_add_friend(self):

	# 	result = self.client.post('/add-friend',
	# 							  method='POST',
	# 							  data={'friend_username': 'HappyMistakes'},
	# 							  follow_redirects=True)

	# 	self.assertIn(b'Visit HappyMistakes', result.data)


def itunes_query(query):

	url = "https://itunes.apple.com/search"
	payload = {
		'term': query,
		'limit': 5,
		'entity': 'podcast',
		'kind': 'podcast-episode'
	}
	resp = requests.get(url, params=payload)
	resp.raise_for_status()

	return resp.content


def gpodder_request():

	from mygpoclient import public
	client = public.PublicClient()
	if client.get_toplist():
		toplist_results = client.get_toplist()

	return toplist_results


class FlaskTestsRequestsCall(TestCase):
	""" Flask tests using mocked API responses. """

	def setUp(self):
		""" Set up. """

		self.client = app.test_client()
		app.config['TESTING'] = True

		with self.client as c:
			with c.session_transaction() as sess:
				sess['username'] = 'HillaryForPres'

	def tearDown(self):

		pass

	def _mock_response(self,
					   status=200,
					   content="CONTENT",
					   json_data=None,
					   raise_for_status=None):

		mock_resp = mock.Mock()

		mock_resp.raise_for_status = mock.Mock()
		if raise_for_status:
			mock_resp.raise_for_status.side_effect = raise_for_status

		mock_resp.status_code = status
		mock_resp.content = content
		if json_data:
			mock_resp.json = mock.Mock(return_value=json_data)

		return mock_resp

	@mock.patch("requests.get")
	def test_itunes_query(self, mock_get):
		""" Test itunes query. """

		mock_resp = self._mock_response(content="FRESH AIR")
		mock_get.return_value = mock_resp

		result = itunes_query('fresh+air')
		self.assertEqual(result, "FRESH AIR")
		self.assertEqual(mock_resp.status_code, 200)


	@mock.patch("requests.get")
	def test_gpodder_request(self, mock_get):
		""" Test gpodder request. """

		mock_resp = self._mock_response()
		mock_get.return_value = mock_resp

		result = gpodder_request()
		self.assertEqual(mock_resp.status_code, 200)


if __name__ == "__main__":
	import unittest

	unittest.main()