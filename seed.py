from model import connect_to_db, db
from model import User, Playlist, Track, TrackPlaylist, Friendship
from server import app


def load_users():

	print("Loading users")

	User.query.delete()

	u1 = User(username='HenryPaw', email='henry@gmail.com', password='123',
			  fname='Henry', lname='Marsman')
	u2 = User(username='MilThePill', email='millie@gmail.com', password='456',
			  fname='Millie', lname='Louise')
	u3 = User(username='BobRoss', email='bob@gmail.com', password='littletrees',
			  fname='Bob', lname='Ross')
	u4 = User(username='NaiveGuy', email='naive@gmail.com', password='password',
			  fname='Dr.', lname='Bayes')

	users = [u1, u2, u3, u4]

	for user in users:
		db.session.add(user)

	# for row in open("seed_data/user_data.csv"):
	# 	row = row.rstrip()
	# 	user_id, username, email, password, fname, lname = row.split(",")

	# 	user = User(user_id=user_id, username=username, email=email,
	# 				password=password, fname=fname, lname=lname)

	# 	db.session.add(user)

	db.session.commit()


def load_playlists():

	print("Loading playlists")

	Playlist.query.delete()

	p1 = Playlist(user_id=1, title='adventure')
	p2 = Playlist(user_id=2, title='stuff to know')
	p3 = Playlist(user_id=3, title='arts')
	p4 = Playlist(user_id=4, title='science')

	playlists = [p1, p2, p3, p4]

	for playlist in playlists:
		db.session.add(playlist)

	# for row in open("seed_data/playlist_data.csv"):
	# 	row = row.rstrip()
	# 	playlist_id, user_id, playlist_name = row.split(",")

	# 	playlist = Playlist(playlist_id=playlist_id, user_id=user_id,
	# 						title=title)

	# 	db.session.add(playlist)

	db.session.commit()


def load_tracks():

	print("Loading tracks")

	Track.query.delete()

	t1 = Track(artist='pups', title='into the woods')
	t2 = Track(artist='sysk', title='pyramids')
	t3 = Track(artist='bob ross', title='mountains')
	t4 = Track(artist='bill nye', title='naive bayes')

	# for row in open("seed_data/podcast_data.csv"):
	# 	row = row.rstrip()
	# 	podcast_id, playlist_id, title = row.split(",")

	# 	track = Track(podcast_id=podcast_id,
	# 				  artist=artist,
	# 				  title=title)

	# 	db.session.add(track)

	tracks = [t1, t2, t3, t4]

	for track in tracks:
		db.session.add(track)

	db.session.commit()


def load_track_playlists():

	print("Loading track-playlists")

	TrackPlaylist.query.delete()

	tp1 = TrackPlaylist(track_id=1, playlist_id=1)
	tp2 = TrackPlaylist(track_id=2, playlist_id=2)
	tp3 = TrackPlaylist(track_id=2, playlist_id=3)
	tp4 = TrackPlaylist(track_id=1, playlist_id=3)
	tp5 = TrackPlaylist(track_id=3, playlist_id=4)

	tps = [tp1, tp2, tp3, tp4, tp5]

	for tp in tps:
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


