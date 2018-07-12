from sqlalchemy import func
from model import connect_to_db, db
from model import User, Playlist, Track, TrackPlaylist, Friendship
from server import app


def load_users():

	print("Loading users")

	User.query.delete()

	# u1 = User(username='HenryPaw', email='henry@gmail.com', password='123',
	# 		  fname='Henry', lname='Marsman')
	# u2 = User(username='MilThePill', email='millie@gmail.com', password='456',
	# 		  fname='Millie', lname='Louise')
	# u3 = User(username='BobRoss', email='bob@gmail.com', password='littletrees',
	# 		  fname='Bob', lname='Ross')
	# u4 = User(username='NaiveGuy', email='naive@gmail.com', password='password',
	# 		  fname='Dr.', lname='Bayes')

	# users = [u1, u2, u3, u4]

	# for user in users:
	# 	db.session.add(user)

	for row in open("seed_data/user_data.csv"):
		row = row.rstrip()
		user_id, username, email, password, fname, lname = row.split(",")

		user = User(user_id=user_id, username=username, email=email,
					password=password, fname=fname, lname=lname)

		db.session.add(user)

	db.session.commit()


def load_playlists():

	print("Loading playlists")

	Playlist.query.delete()

	# p1 = Playlist(user_id=1, title='adventure')
	# p2 = Playlist(user_id=2, title='stuff to know')
	# p3 = Playlist(user_id=3, title='arts')
	# p4 = Playlist(user_id=4, title='science')

	# playlists = [p1, p2, p3, p4]

	# for playlist in playlists:
	# 	db.session.add(playlist)

	for row in open("seed_data/playlist_data.csv"):
		row = row.rstrip()
		playlist_id, user_id, title = row.split(",")

		playlist = Playlist(playlist_id=playlist_id, user_id=user_id,
							title=title)

		db.session.add(playlist)

	db.session.commit()


def load_tracks():

	print("Loading tracks")

	Track.query.delete()

	# t1 = Track(artist='pups', title='into the woods')
	# t2 = Track(artist='sysk', title='pyramids')
	# t3 = Track(artist='bob ross', title='mountains')
	# t4 = Track(artist='bill nye', title='naive bayes')

	# tracks = [t1, t2, t3, t4]

	# for track in tracks:
	# 	db.session.add(track)

	for row in open("seed_data/track_data.csv"):
		row = row.rstrip()
		track_id, artist, title = row.split(",")

		track = Track(track_id=track_id,
					  artist=artist,
					  title=title)

		db.session.add(track)

	db.session.commit()


def load_track_playlists():

	print("Loading track-playlists")

	TrackPlaylist.query.delete()

	# tp1 = TrackPlaylist(track_id=1, playlist_id=1)
	# tp2 = TrackPlaylist(track_id=2, playlist_id=2)
	# tp3 = TrackPlaylist(track_id=2, playlist_id=3)
	# tp4 = TrackPlaylist(track_id=1, playlist_id=3)
	# tp5 = TrackPlaylist(track_id=3, playlist_id=4)

	# tps = [tp1, tp2, tp3, tp4, tp5]

	# for tp in tps:
	# 	db.session.add(tp)

	# db.session.commit()

	for row in open("seed_data/playlist_track_data.csv"):
		row = row.rstrip()
		tp_id, track_id, playlist_id = row.split(",")

		tp = TrackPlaylist(tp_id=tp_id,
					  	   playlist_id=playlist_id,
					  	   track_id=track_id)

		db.session.add(tp)

	db.session.commit()


def load_friendships():

	print("Loading friendships")

	Friendship.query.delete()

	# for row in open("seed_data/relationship_data.csv"):
	# 	row = row.rstrip()
	# 	user_one_id, user_two_id, status = row.split(",")

	# 	friendship = Friendship(friendship_id=friendship_id,
	# 							user_one_id=user_one_id,
	# 							user_two_id=user_two_id)

	# 	db.session.add(friendship)

	# db.session.commit()

	pass


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

# create set_val for playlist, track, friendship


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_playlists()
    load_tracks()
    load_track_playlists()
    # load_friendships()

    set_val_user_id()


