from sqlalchemy import func
from model import connect_to_db, db
from model import User, Playlist, Track, TrackPlaylist, Friendship
from server import app


def load_users():

	print("Loading users")

	User.query.delete()

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

	for row in open("seed_data/playlist_data.csv"):
		row = row.rstrip()
		playlist_id, user_id, title = row.split(",")

		playlist = Playlist(playlist_id=playlist_id, user_id=user_id,
							title=title)

		db.session.add(playlist)

	db.session.commit()


# def load_tracks():

# 	print("Loading tracks")

# 	Track.query.delete()

# 	for row in open("seed_data/track_data.csv"):
# 		row = row.rstrip()
# 		track_id, artist, title = row.split(",")

# 		track = Track(track_id=track_id,
# 					  artist=artist,
# 					  title=title)

# 		db.session.add(track)

# 	db.session.commit()


# def load_track_playlists():

# 	print("Loading track-playlists")

# 	TrackPlaylist.query.delete()

# 	for row in open("seed_data/playlist_track_data.csv"):
# 		row = row.rstrip()
# 		tp_id, track_id, playlist_id = row.split(",")

# 		tp = TrackPlaylist(tp_id=tp_id,
# 					  	   playlist_id=playlist_id,
# 					  	   track_id=track_id)

# 		db.session.add(tp)

# 	db.session.commit()


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


def set_val_playlist_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Playlist.playlist_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('playlists_playlist_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


# def set_val_track_id():
#     """Set value for the next track_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(Track.track_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('tracks_track_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


# def set_val_track_playlist_id():
#     """Set value for the next track_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(TrackPlaylist.tp_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('track_playlist_tp_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()

# create set_val for playlist, track, friendship


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_playlists()
    # load_tracks()
    # load_track_playlists()
    # load_friendships()

    set_val_user_id()
    set_val_playlist_id()
    # set_val_track_id()
    # set_val_track_playlist_id()

