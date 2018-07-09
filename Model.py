from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class User(db.Model):
	"""User model."""

	__tablename__ = "users"

	user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	username = db.Column(db.String(50), unique=True, nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(100), nullable=False)
	fname = db.Column(db.String(50), nullable=False)
	lname = db.Column(db.String(50), nullable=False)

	def __repr__(self):

		s = """
		<User:
		user_id = {}
		username = {}
		email = {}
		password = {}
		name = {} {}>
		""".format(self.user_id, self.username, self.email, self.password,
				   self.fname, self.lname)

		return s


class UserPlaylist(db.Model):
	"""List of user's playlists."""

	__tablename__ = "user_playlists"

	playlist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	playlist_name = db.Column(db.String(70))

	user = db.relationship('User',
							backref=db.backref('user_playlists'))

	podcasts = db.relationship('PlaylistPodcast',
								backref=db.backref('user_playlists'))

	def __repr__(self):

		s = """
		<UserPlaylist:
		playlist_id = {}
		user_id = {}
		playlist_name = {}>
		""".format(self.playlist_id, self.user_id, self.playlist_name)

		return s


class PlaylistPodcast(db.Model):
	"""List of podcasts in a user's playlist."""

	__tablename__ = "playlist_podcasts"

	podcast_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	playlist_id = db.Column(db.Integer,
							db.ForeignKey('user_playlists.playlist_id'))


	def __repr__(self):

		s = """
		<PlaylistPodcast:
		podcast_id = {}
		playlist_id = {}>
		""".format(self.podcast_id, self.playlist_id)

		return s


class UserRelationship(db.Model):
	"""Define relationship between two users."""

	__tablename__ = "user_relationships"
	
	# relationship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_one_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
	user_two_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
	status = db.Column(db.String(20), nullable=False)

	# must be tuple, dictionary
	__table_args__ = (db.UniqueConstraint('user_one_id', 'user_two_id', name='relationship_check'),)


	def __repr__(self):

		s = """
		<UserRelationship:
		user_one_id = {}
		user_two_id = {}
		status = {}>
		""".format(self.user_one_id,
				   self.user_two_id,
				   self.status)

		return s
	

def init_app():
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///users'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def load_data():

	u1 = User(user_id=1, username='henrypcast', email='henry@gmail.com', password='123', fname='henry', lname='marsman')
	u2 = User(user_id=2, username='milliegirl', email='dogemail@gmail.com', password='bacon', fname='millie', lname='louise')

	users = [u1, u2]

	pl1 = UserPlaylist(playlist_id=1, user_id=1, playlist_name='science')
	pl2 = UserPlaylist(playlist_id=2, user_id=1, playlist_name='henryshistory')
	pl3 = UserPlaylist(playlist_id=3, user_id=2, playlist_name='millielistens')
	pl4 = UserPlaylist(playlist_id=4, user_id=2, playlist_name='milandmath')

	playlists = [pl1, pl2, pl3, pl4]

	pcast1 = PlaylistPodcast(playlist_id=1, podcast_id=1)
	pcast2 = PlaylistPodcast(playlist_id=1, podcast_id=2)
	pcast3 = PlaylistPodcast(playlist_id=1, podcast_id=3)
	pcast4 = PlaylistPodcast(playlist_id=2, podcast_id=4)
	pcast5 = PlaylistPodcast(playlist_id=2, podcast_id=5)
	pcast6 = PlaylistPodcast(playlist_id=3, podcast_id=6)
	pcast7 = PlaylistPodcast(playlist_id=3, podcast_id=7)
	pcast8 = PlaylistPodcast(playlist_id=4, podcast_id=8)
	pcast9 = PlaylistPodcast(playlist_id=4, podcast_id=9)
	pcast10 = PlaylistPodcast(playlist_id=4, podcast_id=10)

	pcasts = [pcast1, pcast2, pcast3, pcast4, pcast5, pcast6, pcast7, pcast8, pcast9, pcast10]

	data = []
	data.extend(users)
	data.extend(playlists)
	data.extend(pcasts)

	print(data)

	for d in data:
		db.session.add(d)

	db.session.commit()


if __name__ == "__main__":

	init_app()

