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


class Playlist(db.Model):
	"""List of user's playlists."""

	__tablename__ = "playlists"

	playlist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	title = db.Column(db.String(70))

	user = db.relationship('User',
							backref=db.backref('playlists'))

	tracks = db.relationship('Track',
							 secondary='track_playlist',
							 backref=db.backref('playlists'))


	def __repr__(self):

		s = """
		<UserPlaylist:
		playlist_id = {}
		user_id = {}
		title = {}>
		""".format(self.playlist_id, self.user_id, self.title)

		return s


class Track(db.Model):
	"""List of podcasts in a user's playlist."""

	__tablename__ = "tracks"

	track_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	artist = db.Column(db.String(50))
	title = db.Column(db.String(50), nullable=False)


	def __repr__(self):

		s = """
		<PlaylistPodcast:
		track_id = {}
		artist = {}
		title = {}>
		""".format(self.track_id, self.artist, self.title)

		return s


class TrackPlaylist(db.Model):
	"""Association table between Playlist and Track."""

	__tablename__ = "track_playlist"

	tp_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	playlist_id = db.Column(db.Integer,
							db.ForeignKey('playlists.playlist_id'),
							nullable=False)
	track_id = db.Column(db.Integer,
						 db.ForeignKey('tracks.track_id'),
						 nullable=False)



class Friendship(db.Model):
	"""Define relationship between two users."""

	__tablename__ = "friendships"
	
	friendship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_one_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	user_two_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

	# must be tuple, dictionary
	__table_args__ = (db.UniqueConstraint('user_one_id', 'user_two_id', name='relationship_check'),)

	def __repr__(self):

		s = """
		<UserRelationship:
		Friendship_id = {}
		user_one_id = {}
		user_two_id = {}>
		""".format(self.friendship_id,
				   self.user_one_id,
				   self.user_two_id)

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


if __name__ == "__main__":

	init_app()

