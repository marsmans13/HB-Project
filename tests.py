from server import app
from unittest import TestCase
from model import connect_to_db, db, example_data
from flask import session

class FlaskTestsBasic(TestCase):
	""" Flask tests. """

	def setUp(self):
		""" Do before every test. """

		self.client = app.test_client()

		# Show Flask errors that occur during tests
		app.config['TESTING'] = True

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

	def tearDown(self):

		db.session.close()
		db.drop_all()

	def test_show_playlists(self):
		""" Test show_playlist function. """

		result = self.client.get("/user")
		self.assertIn(b'<h3 class="title"> Playlists </h3>', result.data)


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

		result = self.client.get("/registration")
		self.assertIn(b'<form action="/registration-submit" method="post">',
					  result.data)

	def test_register(self):
		""" Test that db updates to reflect new user. """

		result = self.client.post("/registration-submit",
								 data={'username': 'henrythepup',
								 	   'fname': 'Henry',
								 	   'lname': 'Louise',
								 	   'email': 'henrypup@gmail.com',
								 	   'password': 'bonesforever'},
								 follow_redirects=True)

		self.assertIn(b'Hello, Henry', result.data)


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

	def tearDown(self):
		
		db.session.close()
		db.drop_all()


if __name__ == "__main__":
	import unittest

	unittest.main()
