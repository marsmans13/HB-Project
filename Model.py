from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class User(db.Model):
    """User model."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(256))

    friends = db.relationship('Friendship',
                              primaryjoin="(User.user_id==Friendship.user_one_id)")

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return str(self.user_id)

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
    title = db.Column(db.String(100))

    user = db.relationship('User',
                            backref=db.backref('playlists'))

    tracks = db.relationship('Track',
                             secondary='track_playlist',
                             backref=db.backref('playlists'))

    def __repr__(self):

        s = """
        <Playlist:
        playlist_id = {}
        user_id = {}
        title = {}>
        """.format(self.playlist_id, self.user_id, self.title)

        return s


class Track(db.Model):
    """List of podcasts in a user's playlist."""

    __tablename__ = "tracks"

    track_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    artist = db.Column(db.String(75))
    title = db.Column(db.String(100), nullable=False)
    audio = db.Column(db.String(250), nullable=False)


    def __repr__(self):

        s = """
        <Track:
        track_id = {}
        artist = {}
        title = {}
        audio = {}>
        """.format(self.track_id, self.artist, self.title, self.audio)

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
        <Friendship:
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


def connect_to_db(app, db_uri="postgresql:///users"):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def example_data():
    """ Create example data for the test database. """

    u1 = User(username="HillaryForPres", fname="Hillary", lname="Clinton", email="hclinton@gmail.com", password="bill123")
    u2 = User(username="HappyTrees", fname="Bob", lname="Ross", email="paintwithme@yahoo.com", password="paintbrush456")

    p1 = Playlist(user_id=1, title="NPR")
    p2 = Playlist(user_id=2, title="History")

    t1 = Track(artist='Fresh Air', title='Interview', audio='www.audiofile.com/mp3')
    t2 = Track(artist='How Stuff Works', title='The Pyramids', audio='www.listen.org/mp3')

    db.session.add_all([u1, u2, p1, p2, t1, t2])
    db.session.commit()


    tp1 = TrackPlaylist(playlist_id=1, track_id=1)
    tp2 = TrackPlaylist(playlist_id=2, track_id=2)

    f1 = Friendship(user_one_id=2, user_two_id=1)

    db.session.add_all([tp1, tp2, f1])
    db.session.commit()


if __name__ == "__main__":

    init_app()

